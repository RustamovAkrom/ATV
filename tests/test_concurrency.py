import asyncio
from uuid import UUID, uuid4

import pytest

from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_model import AssetModel
from db.models.assets.manufacturer import Manufacturer
from db.models.org.region import Region
from db.models.org.service import Service


async def _seed_asset_dependencies(dbsession):
    suffix = uuid4().hex[:8]

    region = Region(name=f"ConcurrencyRegion-{suffix}")
    service = Service(name=f"ConcurrencyService-{suffix}", code=f"CS-{suffix}")
    category = AssetCategory(name=f"ConcurrencyCategory-{suffix}", code=f"CC-{suffix}")
    manufacturer = Manufacturer(name=f"ConcurrencyManufacturer-{suffix}")

    dbsession.add_all([region, service, category, manufacturer])
    await dbsession.flush()

    model = AssetModel(
        name=f"ConcurrencyModel-{suffix}",
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
async def test_assign_race_keeps_single_active_assignment(
    client,
    dbsession,
    superadmin_token,
    create_user,
):
    deps = await _seed_asset_dependencies(dbsession)

    owner_1 = await create_user(login="concurrency_owner_1")
    owner_2 = await create_user(login="concurrency_owner_2")

    asset = await _create_asset(client, superadmin_token, deps, "ConcurrencyAsset")
    asset_id = asset["id"]

    start_event = asyncio.Event()
    results = {}

    async def assign_first():
        start_event.set()
        response = await client.post(
            f"/assets/{asset_id}/assign",
            json={"user_id": str(owner_1.id)},
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )
        results["first"] = response.status_code

    async def assign_second():
        await start_event.wait()
        await asyncio.sleep(0.05)  # даём первому начать транзакцию

        response = await client.post(
            f"/assets/{asset_id}/assign",
            json={"user_id": str(owner_2.id)},
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )
        results["second"] = response.status_code

    await asyncio.gather(assign_first(), assign_second())

    # Проверка
    response = await client.get(
        f"/assets/{asset_id}",
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    data = response.json()

    assert results["first"] == 200
    assert results["second"] in (400, 409)  # locked / already assigned

    active = [
        a for a in data['assignments']
        if a ['unassigned_at'] is None
    ]

    assert len(active) == 1


@pytest.mark.anyio
async def test_row_lock_is_applied_for_assignment_repo(
    client,
    dbsession,
    superadmin_token,
    create_user,
):
    deps = await _seed_asset_dependencies(dbsession)
    user = await create_user(login="lock_user")

    asset = await _create_asset(client, superadmin_token, deps, "LockAsset")
    asset_id = asset["id"]

    start_event = asyncio.Event()
    results = {}

    async def hold_lock():
        start_event.set()
        await client.post(
            f"/assets/{asset_id}/assign",
            json={"user_id": str(user.id)},
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )
        await asyncio.sleep(0.3)

    async def try_second():
        await start_event.wait()
        await asyncio.sleep(0.05)

        response = await client.post(
            f"/assets/{asset_id}/assign",
            json={"user_id": str(user.id)},
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )
        results["status"] = response.status_code

    await asyncio.gather(hold_lock(), try_second())

    assert results["status"] in (400, 409)
