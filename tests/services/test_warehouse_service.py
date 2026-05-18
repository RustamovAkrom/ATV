from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from core.exceptions.errors import BadRequest, NotFound
from schemas.assets.warehouses import WarehouseCreateSchema
from schemas.pagination import PaginationParamsSchema
from services.assets.warehouse_service import WarehouseService

pytestmark = pytest.mark.anyio


class _FakeSession:
    def __init__(self):
        self.commits = 0

    async def commit(self):
        self.commits += 1


def _warehouse_obj(name="Warehouse", slug="WH-1"):
    return SimpleNamespace(
        id=uuid4(),
        name=name,
        slug=slug,
        region_id=uuid4(),
        service_id=None,
        manager_user_id=None,
        is_active=True,
        created_at=datetime.now(UTC),
    )


class _MovementObj(SimpleNamespace):
    pass


class _PartObj(SimpleNamespace):
    pass


class _FakeRepo:
    def __init__(self, session):
        self.session = session
        self.warehouses: dict[UUID, SimpleNamespace] = {}
        self.parts: dict[UUID, SimpleNamespace] = {}

    async def list(self, region_id=None, service_id=None, is_active=None, limit=20, offset=0):
        items = list(self.warehouses.values())
        if region_id:
            items = [x for x in items if x.region_id == region_id]
        if service_id:
            items = [x for x in items if x.service_id == service_id]
        if is_active is not None:
            items = [x for x in items if x.is_active == is_active]
        return items[offset: offset + limit], len(items)

    async def create(self, data):
        wh = _warehouse_obj(name=data.get("name"), slug=data.get("slug") or "AUTO")
        region_id = data.get("region_id")
        service_id = data.get("service_id")
        manager_user_id = data.get("manager_user_id")
        wh.region_id = region_id
        wh.service_id = service_id
        wh.manager_user_id = manager_user_id
        self.warehouses[wh.id] = wh
        return wh

    async def get(self, warehouse_id):
        return self.warehouses.get(warehouse_id)

    async def update(self, warehouse_id, data):
        wh = self.warehouses.get(warehouse_id)
        if not wh:
            return None
        for k, v in data.items():
            setattr(wh, k, v)
        return wh

    async def check_slug_exists(self, slug, exclude_id=None):
        slug_u = slug.upper() if isinstance(slug, str) else slug
        for wid, wh in self.warehouses.items():
            if exclude_id and wid == exclude_id:
                continue
            if (wh.slug or "").upper() == slug_u:
                return True
        return False

    async def get_assets_count(self, warehouse_id):
        return 0

    async def delete(self, warehouse_id):
        self.warehouses.pop(warehouse_id, None)

    async def get_warehouse_stock(self, warehouse_id):
        return [
            (uuid4(), "Part1", "P1", 2, 5, 10.0),
            (uuid4(), "Part2", "P2", 10, 5, 20.0),
        ]

    async def record_stock_in(self, **kwargs):
        return _MovementObj(
            id=uuid4(),
            warehouse_id=kwargs["warehouse_id"],
            part_id=kwargs["part_id"],
            movement_type="in",
            quantity=kwargs["quantity"],
            reference_type=kwargs.get("reference_type"),
            reference_id=kwargs.get("reference_id"),
            moved_by=kwargs["moved_by"],
            moved_at=datetime.now(UTC),
        )

    async def record_stock_out(self, **kwargs):
        return _MovementObj(
            id=uuid4(),
            warehouse_id=kwargs["warehouse_id"],
            part_id=kwargs["part_id"],
            movement_type="out",
            quantity=kwargs["quantity"],
            reference_type=kwargs.get("reference_type"),
            reference_id=kwargs.get("reference_id"),
            moved_by=kwargs["moved_by"],
            moved_at=datetime.now(UTC),
        )

    async def get_warehouse_movements(self, warehouse_id, movement_type=None, page=1, size=20):
        items = [
            _MovementObj(
                id=uuid4(),
                warehouse_id=warehouse_id,
                part_id=uuid4(),
                movement_type="in",
                quantity=1,
                reference_type="purchase",
                reference_id=None,
                moved_by=uuid4(),
                moved_at=datetime.now(UTC),
            )
        ]
        if movement_type:
            items = [x for x in items if x.movement_type == movement_type]
        return items, len(items)

    async def get_part_movements(self, warehouse_id, part_id):
        return [
            _MovementObj(
                id=uuid4(),
                warehouse_id=warehouse_id,
                part_id=part_id,
                movement_type="in",
                quantity=1,
                reference_type="purchase",
                reference_id=None,
                moved_by=uuid4(),
                moved_at=datetime.now(UTC),
            )
        ]

    async def list_parts(self, warehouse_id=None, page=1, size=20):
        items = list(self.parts.values())
        return items[:size], len(items)

    async def create_part(self, name, slug=None, description=None, unit_price=None):
        part = _PartObj(
            id=uuid4(),
            name=name,
            slug=slug or "PRT",
            description=description,
            unit_price=unit_price,
            created_at=datetime.now(UTC),
        )
        self.parts[part.id] = part
        return part

    async def get_part_by_id(self, part_id):
        return self.parts.get(part_id)

    async def update_part(self, part_id, data):
        part = self.parts.get(part_id)
        for k, v in data.items():
            setattr(part, k, v)
        return part

    async def delete_part(self, part_id):
        self.parts.pop(part_id, None)


@pytest.fixture
def warehouse_service(monkeypatch):
    repo = _FakeRepo(_FakeSession())
    asset_repo = SimpleNamespace(get_by_id=None, flush=None)
    events = SimpleNamespace(asset_moved_to_warehouse=None)
    return WarehouseService(repo, asset_repo, events)

class TestWarehouseService:
    async def test_create_list_get_update_delete_warehouse(self, warehouse_service):
        region_id = uuid4()
        created = await warehouse_service.create_warehouse(
            WarehouseCreateSchema(name="Test Warehouse", region_id=region_id, slug="TWH001")
        )
        assert created.name == "Test Warehouse"

        _listed_items, listed_total = await warehouse_service.list_warehouses(
            PaginationParamsSchema(page=1, limit=10)
        )
        assert listed_total >= 1

        got = await warehouse_service.get_warehouse(created.id)
        assert got.slug == "TWH001"

        updated = await warehouse_service.update_warehouse(created.id, {"name": "Updated", "is_active": False})
        assert updated.name == "Updated"
        assert updated.is_active is False

        await warehouse_service.delete_warehouse(created.id)
        with pytest.raises(NotFound):
            await warehouse_service.get_warehouse(created.id)

    async def test_get_update_delete_not_found(self, warehouse_service):
        fake_id = uuid4()
        with pytest.raises(NotFound):
            await warehouse_service.get_warehouse(fake_id)
        with pytest.raises(NotFound):
            await warehouse_service.update_warehouse(fake_id, {"name": "x"})
        with pytest.raises(NotFound):
            await warehouse_service.delete_warehouse(fake_id)

    async def test_stock_and_movements(self, warehouse_service):
        region_id = uuid4()
        wh = await warehouse_service.create_warehouse(
            WarehouseCreateSchema(name="Stock WH", region_id=region_id)
        )
        warehouse_id = wh.id
        part_id = uuid4()
        user_id = uuid4()

        stock = await warehouse_service.get_warehouse_stock(warehouse_id)
        assert len(stock) == 2
        assert stock[0]["status"] in {"low", "ok"}

        stock_in = await warehouse_service.record_stock_in(warehouse_id, part_id, 5, user_id)
        assert stock_in["movement_type"] == "in"

        stock_out = await warehouse_service.record_stock_out(warehouse_id, part_id, 2, user_id)
        assert stock_out["movement_type"] == "out"

        movements = await warehouse_service.get_warehouse_movements(warehouse_id, movement_type="in")
        assert "items" in movements

        part_moves = await warehouse_service.get_part_movements(warehouse_id, part_id)
        assert len(part_moves) >= 1

    async def test_stock_validation_error(self, warehouse_service):
        warehouse_id = uuid4()
        part_id = uuid4()
        user_id = uuid4()
        with pytest.raises(BadRequest):
            await warehouse_service.record_stock_in(warehouse_id, part_id, 0, user_id)
        with pytest.raises(BadRequest):
            await warehouse_service.record_stock_out(warehouse_id, part_id, -1, user_id)

    async def test_parts_crud(self, warehouse_service):
        created = await warehouse_service.create_part("Part A", slug="PA", unit_price=12.5)
        part_id = UUID(created["id"])

        listed = await warehouse_service.list_parts(page=1, size=10)
        assert listed["total"] >= 1

        part = await warehouse_service.get_part(part_id)
        assert part["name"] == "Part A"

        updated = await warehouse_service.update_part(part_id, {"name": "Part B"})
        assert updated["name"] == "Part B"

        await warehouse_service.delete_part(part_id)
        with pytest.raises(NotFound):
            await warehouse_service.get_part(part_id)
