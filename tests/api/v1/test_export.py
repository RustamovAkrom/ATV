from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.security.passwords import hash_password
from core.security.rbac.permissions import Permissions
from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_model import AssetModel
from db.models.assets.manufacturer import Manufacturer
from db.models.enums import UserStatus
from db.models.org.region import Region
from db.models.org.service import Service
from db.models.users.permission import Permission, Role
from db.models.users.user import User
from services.assets.export_service import ExportService


async def _seed_asset_dependencies(dbsession):
    suffix = uuid4().hex[:8]
    region = Region(name=f"ExportRegion-{suffix}")
    service = Service(name=f"ExportService-{suffix}", slug=f"ES-{suffix}")
    category = AssetCategory(name=f"ExportCategory-{suffix}", slug=f"EC-{suffix}")
    manufacturer = Manufacturer(name=f"ExportManufacturer-{suffix}")
    dbsession.add_all([region, service, category, manufacturer])
    await dbsession.flush()
    model = AssetModel(
        name=f"ExportModel-{suffix}",
        manufacturer_id=manufacturer.id,
        category_id=category.id,
    )
    dbsession.add(model)
    await dbsession.commit()
    return {"region": region, "service": service, "model": model}


async def _create_asset(client, token: str, deps: dict, name: str):
    response = await client.post(
        "/api/v1/assets/",
        json={
            "name": name,
            "model_id": str(deps["model"].id),
            "region_id": str(deps["region"].id),
            "service_id": str(deps["service"].id),
            "serial_number": f"SN-{uuid4().hex[:8]}",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    return response.json()


async def _create_role_user(dbsession, role_slug: str, login: str):
    # Get or create the role with permissions loaded
    role = await dbsession.scalar(
        select(Role)
        .options(selectinload(Role.permissions))
        .where(Role.slug == role_slug)
    )
    if not role:
        role = Role(name=role_slug.upper(), slug=role_slug, permissions=[])
        dbsession.add(role)
        await dbsession.flush()
        # Reload with selectinload
        role = await dbsession.scalar(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.slug == role_slug)
        )

    # Assign appropriate permissions based on role slug
    permissions_to_assign = []

    if role_slug == "analyst":
        # Analyst role should have ASSETS_EXPORT permission
        perm = await dbsession.scalar(
            select(Permission).where(Permission.slug == Permissions.ASSETS_EXPORT)
        )
        if not perm:
            perm = Permission(name="Export Assets", slug=Permissions.ASSETS_EXPORT)
            dbsession.add(perm)
            await dbsession.flush()
        permissions_to_assign.append(perm)
    elif role_slug == "operator":
        # Operator role should NOT have ASSETS_EXPORT permission
        # Get ASSETS_VIEW permission if it exists
        perm = await dbsession.scalar(
            select(Permission).where(Permission.slug == Permissions.ASSETS_VIEW)
        )
        if not perm:
            perm = Permission(name="View Assets", slug=Permissions.ASSETS_VIEW)
            dbsession.add(perm)
            await dbsession.flush()
        permissions_to_assign.append(perm)

    # Update permissions directly on the loaded role object
    if role.permissions is None:
        role.permissions = []
    role.permissions = permissions_to_assign
    await dbsession.flush()

    user = User(
        login=login,
        password_hash=hash_password("password"),
        email=f"{login}@test.com",
        phone=f"+9989{uuid4().hex[:8]}",
        role_id=role.id,
        status=UserStatus.ACTIVE.value,
    )
    dbsession.add(user)
    await dbsession.commit()
    return user


@pytest.mark.anyio
async def test_csv_export(client, dbsession, superadmin_token):
    deps = await _seed_asset_dependencies(dbsession)
    await _create_asset(client, superadmin_token, deps, "CsvExportAsset")

    response = await client.get(
        "/api/v1/assets/export",
        params={"format": "csv", "search": "CsvExportAsset"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "CsvExportAsset" in response.text


@pytest.mark.anyio
async def test_export_row_limit(client, dbsession, superadmin_token, monkeypatch):
    deps = await _seed_asset_dependencies(dbsession)
    await _create_asset(client, superadmin_token, deps, "RowLimitOne")
    await _create_asset(client, superadmin_token, deps, "RowLimitTwo")
    monkeypatch.setattr(ExportService, "MAX_EXPORT_ROWS", 1)

    response = await client.get(
        "/api/v1/assets/export",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_export_permissions(client, dbsession, superadmin_token):
    deps = await _seed_asset_dependencies(dbsession)
    await _create_asset(client, superadmin_token, deps, "PermissionExportAsset")
    operator = await _create_role_user(dbsession, "operator", "export_operator")
    analyst = await _create_role_user(dbsession, "analyst", "export_analyst")

    operator_login = await client.post(
        "/api/v1/auth/login",
        data={"username": operator.login, "password": "password"},
    )
    assert operator_login.status_code == 200
    operator_token = operator_login.cookies.get("access_token")

    analyst_login = await client.post(
        "/api/v1/auth/login",
        data={"username": analyst.login, "password": "password"},
    )
    assert analyst_login.status_code == 200
    analyst_token = analyst_login.cookies.get("access_token")

    operator_response = await client.get(
        "/api/v1/assets/export",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {operator_token}"},
    )
    assert operator_response.status_code == 403

    analyst_response = await client.get(
        "/api/v1/assets/export",
        params={"format": "json", "search": "PermissionExportAsset"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert analyst_response.status_code == 200
    assert "PermissionExportAsset" in analyst_response.text
