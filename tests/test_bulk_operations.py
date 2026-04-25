from uuid import uuid4

import pytest

from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_model import AssetModel
from db.models.assets.manufacturer import Manufacturer
from db.models.org.region import Region
from db.models.org.service import Service


async def _seed_asset_dependencies(dbsession):
    suffix = uuid4().hex[:8]
    region = Region(name=f"BulkRegion-{suffix}")
    service = Service(name=f"BulkService-{suffix}", code=f"BS-{suffix}")
    category = AssetCategory(name=f"BulkCategory-{suffix}", code=f"BC-{suffix}")
    manufacturer = Manufacturer(name=f"BulkManufacturer-{suffix}")
    dbsession.add_all([region, service, category, manufacturer])
    await dbsession.flush()
    model = AssetModel(
        name=f"BulkModel-{suffix}",
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
async def test_bulk_partial_success(client, dbsession, superadmin_token, create_user):
    deps = await _seed_asset_dependencies(dbsession)
    user = await create_user(login="bulk_hardening_owner")
    asset_1 = await _create_asset(client, superadmin_token, deps, "BulkHardAssetOne")
    asset_2 = await _create_asset(client, superadmin_token, deps, "BulkHardAssetTwo")

    response = await client.post(
        "/assets/bulk/assign",
        json={
            "asset_ids": [asset_1["id"], asset_2["id"], str(uuid4())],
            "user_id": str(user.id),
        },
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["success"]) == 2
    assert len(body["failed"]) == 1
    assert "error" in body["failed"][0]


@pytest.mark.anyio
async def test_bulk_limit_exceeded(client, dbsession, superadmin_token, create_user):
    deps = await _seed_asset_dependencies(dbsession)
    user = await create_user(login="bulk_limit_owner")
    asset_ids = []
    for idx in range(101):
        asset = await _create_asset(client, superadmin_token, deps, f"BulkLimitAsset{idx}")
        asset_ids.append(asset["id"])

    response = await client.post(
        "/assets/bulk/assign",
        json={"asset_ids": asset_ids, "user_id": str(user.id)},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 400


@pytest.mark.anyio
async def test_bulk_invalid_items_return_failed_entries(client, dbsession, superadmin_token):
    deps = await _seed_asset_dependencies(dbsession)
    asset = await _create_asset(client, superadmin_token, deps, "BulkStatusAsset")

    response = await client.post(
        "/assets/bulk/status",
        json={"asset_ids": [asset["id"], str(uuid4())], "status": "archived"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["success"]) == 1
    assert len(body["failed"]) == 1
