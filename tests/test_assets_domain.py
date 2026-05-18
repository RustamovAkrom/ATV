from uuid import UUID, uuid4

import pytest
import io
from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_model import AssetModel
from db.models.assets.manufacturer import Manufacturer
from db.models.documents.document import Document
from db.models.documents.document_file import DocumentFile
from db.models.org.region import Region
from db.models.org.service import Service
from db.models.warehouse.warehouse import Warehouse


async def _seed_asset_dependencies(dbsession):
    suffix = uuid4().hex[:8]

    region = Region(name=f"Region-{suffix}")
    other_region = Region(name=f"OtherRegion-{suffix}")
    service = Service(name=f"Service-{suffix}", slug=f"SVC-{suffix}")
    other_service = Service(name=f"OtherService-{suffix}", slug=f"OSVC-{suffix}")
    category = AssetCategory(name=f"Category-{suffix}", slug=f"CAT-{suffix}")
    manufacturer = Manufacturer(name=f"Manufacturer-{suffix}")

    dbsession.add_all(
        [region, other_region, service, other_service, category, manufacturer]
    )
    await dbsession.flush()

    model = AssetModel(
        name=f"Model-{suffix}",
        manufacturer_id=manufacturer.id,
        category_id=category.id,
    )
    dbsession.add(model)
    await dbsession.flush()

    warehouse = Warehouse(
        name=f"Warehouse-{suffix}",
        slug=f"WH-{suffix}",
        region_id=region.id,
        service_id=service.id,
        is_active=True,
    )
    target_warehouse = Warehouse(
        name=f"TargetWarehouse-{suffix}",
        slug=f"TWH-{suffix}",
        region_id=region.id,
        service_id=service.id,
        is_active=True,
    )
    incompatible_warehouse = Warehouse(
        name=f"BadWarehouse-{suffix}",
        slug=f"BWH-{suffix}",
        region_id=other_region.id,
        service_id=other_service.id,
        is_active=True,
    )
    dbsession.add_all([warehouse, target_warehouse, incompatible_warehouse])
    await dbsession.commit()

    return {
        "region": region,
        "other_region": other_region,
        "service": service,
        "other_service": other_service,
        "model": model,
        "warehouse": warehouse,
        "target_warehouse": target_warehouse,
        "incompatible_warehouse": incompatible_warehouse,
    }


async def _create_asset(client, token: str, deps: dict, name: str | None = None):
    payload = {
        "name": name or f"Asset-{uuid4().hex[:6]}",
        "model_id": str(deps["model"].id),
        "region_id": str(deps["region"].id),
        "service_id": str(deps["service"].id),
        "serial_number": f"SN-{uuid4().hex[:8]}",
    }
    response = await client.post(
        "/assets/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    return response.json()


@pytest.mark.anyio
async def test_asset_assignment_flow(client, dbsession, analytics_tokens, create_user):
    superadmin_token = analytics_tokens["superadmin"]
    deps = await _seed_asset_dependencies(dbsession)
    owner_1 = await create_user(login="asset_owner_1")
    owner_2 = await create_user(login="asset_owner_2")
    asset = await _create_asset(client, superadmin_token, deps)

    request_assignment = await client.post(
        f"/assets/{asset['id']}/approval-requests/assignment",
        json={"user_id": str(owner_1.id)},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert request_assignment.status_code == 200
    approval_id = request_assignment.json()["id"]

    response = await client.post(
        f"/approvals/{approval_id}/approve",
        json={"comment": "approve assignment"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200

    assigned_asset = await client.get(
        f"/assets/{asset['id']}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert assigned_asset.status_code == 200
    assert assigned_asset.json()["owner"]["id"] == str(owner_1.id)

    request_reassign = await client.post(
        f"/assets/{asset['id']}/approval-requests/assignment",
        json={"user_id": str(owner_2.id)},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert request_reassign.status_code == 200
    response = await client.post(
        f"/approvals/{request_reassign.json()['id']}/approve",
        json={"comment": "approve reassignment"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200

    reassigned_asset = await client.get(
        f"/assets/{asset['id']}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert reassigned_asset.status_code == 200
    assert reassigned_asset.json()["owner"]["id"] == str(owner_2.id)

    history = await client.get(
        f"/assets/{asset['id']}/history",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert history.status_code == 200
    actions = {entry["action"] for entry in history.json()}
    assert "assigned" in actions


@pytest.mark.anyio
async def test_repair_lifecycle_flow(client, dbsession, analytics_tokens):
    superadmin_token = analytics_tokens["superadmin"]
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, name="RepairAsset")

    reported = await client.post(
        f"/assets/{asset['id']}/repair/report",
        json={"description": "Broken display"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert reported.status_code == 200
    repair = reported.json()
    assert repair["status"] == "reported"

    started = await client.post(
        f"/assets/{asset['id']}/repair/{repair['id']}/start",
        json={
            "labor_cost": "50.00",
            "parts": [
                {"part_name": "Display cable", "quantity": 1, "unit_price": "20.00"},
                {"part_name": "Bracket", "quantity": 2, "unit_price": "5.00"},
            ],
        },
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert started.status_code == 200
    started_body = started.json()
    assert started_body["status"] == "in_progress"
    assert started_body["total_cost"] == "80.00"

    asset_in_repair = await client.get(
        f"/assets/{asset['id']}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert asset_in_repair.status_code == 200
    assert asset_in_repair.json()["status"] == "in_repair"
    assert asset_in_repair.json()["failure_count"] == 0

    completion_request = await client.post(
        f"/assets/{asset['id']}/approval-requests/repair/{repair['id']}/complete",
        json={"labor_cost": "75.00"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert completion_request.status_code == 200
    completed = await client.post(
        f"/approvals/{completion_request.json()['id']}/approve",
        json={"comment": "complete repair"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert completed.status_code == 200

    repaired_asset = await client.get(
        f"/assets/{asset['id']}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert repaired_asset.status_code == 200
    repaired_body = repaired_asset.json()
    assert repaired_body["status"] == "active"
    assert repaired_body["last_repair_date"] is not None
    assert repaired_body["failure_count"] == 1


@pytest.mark.anyio
async def test_document_attach_and_delete_flow(client, dbsession, analytics_tokens):
    superadmin_token = analytics_tokens["superadmin"]
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, name="DocumentAsset")

    attached = await client.post(
        f"/assets/{asset['id']}/documents/",
        data={"title": "Warranty", "document_type": "warranty"},
        files=[
            (
                "files",
                ("warranty.pdf", io.BytesIO(b"fake pdf content"), "application/pdf"),
            )
        ],
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert attached.status_code == 200
    document = attached.json()
    assert document["title"] == "Warranty"
    assert len(document["files"]) == 1

    deleted = await client.delete(
        f"/assets/{asset['id']}/documents/{document['id']}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert deleted.status_code == 200

    document_count = await dbsession.scalar(select(func.count()).select_from(Document))
    file_count = await dbsession.scalar(select(func.count()).select_from(DocumentFile))
    assert document_count == 0
    assert file_count == 0



@pytest.mark.anyio
async def test_locked_asset_transfer_is_rejected(client, dbsession, analytics_tokens):
    superadmin_token = analytics_tokens["superadmin"]
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(
        client, superadmin_token, deps, name="LockedTransferAsset"
    )

    db_asset = await dbsession.scalar(
        select(Asset).where(Asset.id == UUID(asset["id"]))
    )
    db_asset.is_transfer_locked = True
    await dbsession.commit()

    response = await client.post(
        f"/assets/{asset['id']}/approval-requests/transfer",
        json={
            "from_warehouse_id": str(deps["warehouse"].id),
            "to_warehouse_id": str(deps["target_warehouse"].id),
        },
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 400
