from uuid import uuid4

import pytest
from sqlalchemy import select

from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_model import AssetModel
from db.models.assets.asset_transfer import AssetTransfer
from db.models.assets.manufacturer import Manufacturer
from db.models.org.region import Region
from db.models.org.service import Service


async def _seed_asset_dependencies(dbsession):
    suffix = uuid4().hex[:8]
    region = Region(name=f"ApprovalRegion-{suffix}")
    service = Service(name=f"ApprovalService-{suffix}", code=f"APS-{suffix}")
    category = AssetCategory(name=f"ApprovalCategory-{suffix}", code=f"APC-{suffix}")
    manufacturer = Manufacturer(name=f"ApprovalManufacturer-{suffix}")
    dbsession.add_all([region, service, category, manufacturer])
    await dbsession.flush()

    model = AssetModel(
        name=f"ApprovalModel-{suffix}",
        manufacturer_id=manufacturer.id,
        category_id=category.id,
    )
    dbsession.add(model)
    await dbsession.commit()
    return {"region": region, "service": service, "model": model}


async def _create_asset(client, token: str, deps: dict, name: str):
    response = await client.post(
        "/assets/",
        json={
            "name": name,
            "type": "laptop",
            "model_id": str(deps["model"].id),
            "region_id": str(deps["region"].id),
            "service_id": str(deps["service"].id),
            "asset_tag": f"AT-{uuid4().hex[:6]}",
            "serial_number": f"SN-{uuid4().hex[:8]}",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    return response.json()


@pytest.mark.anyio
async def test_create_and_approve_archive_request(client, dbsession, superadmin_token, approver_token):
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, "NeedsApprovalArchive")

    created = await client.post(
        "/approvals/",
        json={
            "entity_type": "asset_archive",
            "entity_id": asset["id"],
            "action": "archive",
            "payload": {},
        },
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert created.status_code == 200
    approval = created.json()
    assert approval["status"] == "pending"

    approved = await client.post(
        f"/approvals/{approval['id']}/approve",
        json={"comment": "Approved archive"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    asset_response = await client.get(
        f"/assets/{asset['id']}",
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert asset_response.status_code == 200
    assert asset_response.json()["status"] == "archived"


@pytest.mark.anyio
async def test_reject_transfer_approval_request(client, dbsession, superadmin_token, approver_token):
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, "NeedsApprovalTransfer")

    created = await client.post(
        "/approvals/",
        json={
            "entity_type": "asset_transfer",
            "entity_id": asset["id"],
            "action": "create_transfer",
            "payload": {
                "to_service_id": str(deps["service"].id),
                "comment": "Pending approval",
            },
        },
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert created.status_code == 200

    rejected = await client.post(
        f"/approvals/{created.json()['id']}/reject",
        json={"comment": "Not needed"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    transfers = await dbsession.execute(
        select(AssetTransfer).where(AssetTransfer.asset_id == asset["id"])
    )
    assert transfers.scalars().all() == []


@pytest.mark.anyio
async def test_bulk_assign_partial_success(
    client, dbsession, superadmin_token, create_user
):
    deps = await _seed_asset_dependencies(dbsession)
    user = await create_user(login="bulk_assign_owner")
    asset_1 = await _create_asset(client, superadmin_token, deps, "BulkAssignOne")
    asset_2 = await _create_asset(client, superadmin_token, deps, "BulkAssignTwo")

    response = await client.post(
        "/assets/bulk/assign",
        json={
            "asset_ids": [asset_1["id"], asset_2["id"], str(uuid4())],
            "user_id": str(user.id),
        },
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["success"]) == 2
    assert len(data["failed"]) == 1


@pytest.mark.anyio
async def test_export_assets_csv_with_filter(client, dbsession, superadmin_token):
    deps = await _seed_asset_dependencies(dbsession)
    await _create_asset(client, superadmin_token, deps, "ExportTargetLaptop")
    await _create_asset(client, superadmin_token, deps, "OtherAsset")

    response = await client.get(
        "/assets/export",
        params={"format": "csv", "search": "ExportTarget"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "ExportTargetLaptop" in response.text
    assert "OtherAsset" not in response.text


@pytest.mark.anyio
async def test_export_assets_json_returns_filtered_payload(
    client, dbsession, superadmin_token
):
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, "JsonExportAsset")

    response = await client.get(
        "/assets/export",
        params={"format": "json", "search": "JsonExportAsset"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "JsonExportAsset" in response.text
    assert asset["id"] in response.text
