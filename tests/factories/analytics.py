from decimal import Decimal
from uuid import uuid4

from sqlalchemy import insert, select
from sqlalchemy.orm import selectinload

from core.security.passwords import hash_password
from core.security.rbac.permissions import ROLE_PERMISSIONS
from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_class import AssetClass
from db.models.assets.asset_history import AssetHistory
from db.models.assets.asset_model import AssetModel
from db.models.assets.asset_transfer import AssetTransfer
from db.models.assets.manufacturer import Manufacturer
from db.models.enums import AssetStatus, RepairStatus, TransferStatus, UserStatus
from db.models.org.region import Region
from db.models.org.service import Service, region_services
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart
from db.models.users.permission import Permission, Role
from db.models.users.user import User
from db.models.warehouse.warehouse import Warehouse


async def ensure_role_with_permissions(dbsession, role_code: str) -> Role:
    # Query with explicit selectinload to avoid lazy loading issues
    result = await dbsession.execute(
        select(Role)
        .where(Role.code == role_code)
        .options(selectinload(Role.permissions))
    )
    role = result.scalar_one_or_none()
    if role is None:
        role = Role(name=role_code.title(), code=role_code)
        dbsession.add(role)
        await dbsession.flush()
        # Refresh to load relationships after creation
        await dbsession.refresh(role, ["permissions"])

    for permission_code in ROLE_PERMISSIONS.get(role_code, set()):
        perm_result = await dbsession.execute(
            select(Permission).where(Permission.code == permission_code)
        )
        permission = perm_result.scalar_one_or_none()
        if permission is None:
            permission = Permission(name=permission_code, code=permission_code)
            dbsession.add(permission)
            await dbsession.flush()
        if permission not in role.permissions:
            role.permissions.append(permission)

    await dbsession.flush()
    return role


async def create_user_with_role(
    dbsession, *, login_prefix: str, role_code: str, password: str = "password"
) -> User:
    role = await ensure_role_with_permissions(dbsession, role_code)
    suffix = uuid4().hex[:8]
    user = User(
        login=f"{login_prefix}_{suffix}",
        password_hash=hash_password(password),
        email=f"{login_prefix}_{suffix}@test.local",
        phone=f"+99890{suffix[:7]}",
        role_id=role.id,
        status=UserStatus.ACTIVE.value,
        first_name=login_prefix.title(),
        last_name="User",
    )
    dbsession.add(user)
    await dbsession.flush()
    return user


async def create_org_graph(dbsession):
    manufacturer = Manufacturer(
        name=f"Manufacturer-{uuid4().hex[:6]}", code=f"mfg-{uuid4().hex[:6]}"
    )
    category = AssetCategory(
        name=f"Category-{uuid4().hex[:6]}", code=f"cat-{uuid4().hex[:6]}"
    )
    asset_class = AssetClass(
        name=f"Class-{uuid4().hex[:6]}", code=f"class-{uuid4().hex[:6]}"
    )
    region = Region(
        name=f"Region-{uuid4().hex[:6]}",
        latitude=41.31,
        longitude=69.28,
        geojson={"type": "Point", "coordinates": [69.28, 41.31]},
    )
    service = Service(name=f"Service-{uuid4().hex[:6]}", code=f"svc-{uuid4().hex[:6]}")
    dbsession.add_all([manufacturer, category, asset_class, region, service])
    await dbsession.flush()
    await dbsession.execute(
        insert(region_services).values(region_id=region.id, service_id=service.id)
    )

    model = AssetModel(
        name=f"Model-{uuid4().hex[:6]}",
        code=f"model-{uuid4().hex[:6]}",
        manufacturer_id=manufacturer.id,
        category_id=category.id,
        lifetime_years=5,
        warranty_months=24,
    )
    dbsession.add(model)
    await dbsession.flush()

    warehouse = Warehouse(
        name=f"Warehouse-{uuid4().hex[:6]}",
        code=f"wh-{uuid4().hex[:6]}",
        region_id=region.id,
        service_id=service.id,
        is_active=True,
    )
    dbsession.add(warehouse)
    await dbsession.flush()

    return {
        "manufacturer": manufacturer,
        "category": category,
        "asset_class": asset_class,
        "region": region,
        "service": service,
        "model": model,
        "warehouse": warehouse,
    }


async def create_asset(
    dbsession,
    *,
    graph: dict,
    owner: User | None = None,
    name: str = "Asset",
    status: AssetStatus = AssetStatus.ACTIVE,
    purchase_cost: Decimal | int = 1000,
) -> Asset:
    suffix = uuid4().hex[:6]
    normalized_status = status
    if owner and status == AssetStatus.ACTIVE:
        normalized_status = AssetStatus.ASSIGNED

    asset = Asset(
        name=f"{name}-{suffix}",
        type="laptop",
        model_id=graph["model"].id,
        class_id=graph["asset_class"].id,
        region_id=graph["region"].id,
        service_id=graph["service"].id,
        current_warehouse_id=graph["warehouse"].id,
        owner_id=owner.id if owner else None,
        status=normalized_status,
        asset_tag=f"AT-{suffix}",
        serial_number=f"SN-{uuid4().hex[:10]}",
        condition_percent=95,
        purchase_cost=Decimal(str(purchase_cost)),
        meta={"source": "test"},
    )
    dbsession.add(asset)
    await dbsession.flush()
    return asset


async def create_assignment(
    dbsession, *, asset: Asset, user: User, assigned_at, unassigned_at=None
) -> AssetAssignment:
    assignment = AssetAssignment(
        asset_id=asset.id,
        user_id=user.id,
        assigned_at=assigned_at,
        unassigned_at=unassigned_at,
    )
    dbsession.add(assignment)
    await dbsession.flush()
    return assignment


async def create_transfer(
    dbsession,
    *,
    asset: Asset,
    created_by: User,
    graph: dict,
    created_at,
    status: TransferStatus = TransferStatus.PENDING,
    transferred_at=None,
) -> AssetTransfer:
    transfer = AssetTransfer(
        asset_id=asset.id,
        created_by_id=created_by.id,
        status=status,
        from_warehouse_id=graph["warehouse"].id,
        to_warehouse_id=graph["warehouse"].id,
        from_service_id=graph["service"].id,
        to_service_id=graph["service"].id,
        created_at=created_at,
        transferred_at=transferred_at,
        comment="test transfer",
    )
    dbsession.add(transfer)
    await dbsession.flush()
    return transfer


async def create_repair(
    dbsession,
    *,
    asset: Asset,
    reported_by: User,
    created_at,
    status: RepairStatus = RepairStatus.REPORTED,
    labor_cost: Decimal | int = 100,
    parts_cost: Decimal | int = 50,
) -> Repair:
    repair = Repair(
        asset_id=asset.id,
        reported_by_id=reported_by.id,
        description="test repair",
        status=status,
        created_at=created_at,
        labor_cost=Decimal(str(labor_cost)),
    )
    dbsession.add(repair)
    await dbsession.flush()

    repair_part = RepairPart(
        repair_id=repair.id,
        part_name="part",
        quantity=1,
        unit_price=Decimal(str(parts_cost)),
    )
    dbsession.add(repair_part)
    await dbsession.flush()
    return repair


async def create_history(
    dbsession, *, asset: Asset, user: User, action: str, description: str, created_at
) -> AssetHistory:
    history = AssetHistory(
        asset_id=asset.id,
        user_id=user.id,
        action=action,
        description=description,
        created_at=created_at,
    )
    dbsession.add(history)
    await dbsession.flush()
    return history
