from uuid import uuid4

import pytest
from sqlalchemy import select

from db.models.approvals.approval_request import ApprovalRequest
from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_model import AssetModel
from db.models.assets.manufacturer import Manufacturer
from db.models.org.region import Region
from db.models.org.service import Service


async def _seed_asset_dependencies(dbsession):
    suffix = uuid4().hex[:8]
    region = Region(name=f"ApprovalHardRegion-{suffix}")
    service = Service(name=f"ApprovalHardService-{suffix}", code=f"AHS-{suffix}")
    category = AssetCategory(
        name=f"ApprovalHardCategory-{suffix}", code=f"AHC-{suffix}"
    )
    manufacturer = Manufacturer(name=f"ApprovalHardManufacturer-{suffix}")
    dbsession.add_all([region, service, category, manufacturer])
    await dbsession.flush()
    model = AssetModel(
        name=f"ApprovalHardModel-{suffix}",
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
async def test_double_approve_fails(client, dbsession, superadmin_token, approver_token):
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, "DoubleApproveAsset")

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
    approval_id = created.json()["id"]

    first = await client.post(
        f"/approvals/{approval_id}/approve",
        json={"comment": "approve once"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert first.status_code == 200
    assert first.json()["executed"] is True

    second = await client.post(
        f"/approvals/{approval_id}/approve",
        json={"comment": "approve twice"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert second.status_code == 400


@pytest.mark.anyio
async def test_replay_after_approve_fails(client, dbsession, superadmin_token, approver_token):
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, "ReplayApprovalAsset")

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
    approval_id = created.json()["id"]

    approved = await client.post(
        f"/approvals/{approval_id}/approve",
        json={"comment": "done"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert approved.status_code == 200

    replay = await client.post(
        f"/approvals/{approval_id}/reject",
        json={"comment": "too late"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert replay.status_code == 400

    approval = await dbsession.scalar(
        select(ApprovalRequest).where(ApprovalRequest.id == approval_id)
    )
    assert approval is not None
    assert approval.executed is True


@pytest.mark.anyio
async def test_invalid_approval_payload_fails(client, dbsession, superadmin_token):
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(
        client, superadmin_token, deps, "InvalidApprovalPayloadAsset"
    )

    response = await client.post(
        "/approvals/",
        json={
            "entity_type": "repair",
            "entity_id": asset["id"],
            "action": "complete_repair",
            "payload": {"labor_cost": "10.00"},
        },
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 400
