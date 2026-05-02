from uuid import UUID

from core.exceptions.errors import BadRequest, NotFound
from repositories.warehouse.warehouse_repo import WarehouseRepository
from schemas.assets.warehouses import WarehouseMoveRequest
from core.events.warehouse_events import WarehouseEventService
from schemas.auth.auth import CurrentUserSchema


class WarehouseService:
    def __init__(
        self,
        repo: WarehouseRepository,
        warehouse_events: WarehouseEventService
    ):
        self.repo = repo
        self.warehouse_events = warehouse_events

    async def move_asset_to_warehouse(
        self, asset_id: UUID, data: WarehouseMoveRequest, actor: CurrentUserSchema
    ) -> UUID:
        asset = await self.repo.get_asset(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        warehouse = await self.repo.get_warehouse(data.warehouse_id)
        if not warehouse:
            raise NotFound("Warehouse not found")

        if not warehouse.is_active:
            raise BadRequest("Warehouse is inactive")

        if asset.region_id is not None and asset.region_id != warehouse.region_id:
            raise BadRequest("Warehouse region is incompatible with asset region")

        if (
            asset.service_id is not None
            and warehouse.service_id is not None
            and asset.service_id != warehouse.service_id
        ):
            raise BadRequest("Warehouse service is incompatible with asset service")

        asset.current_warehouse_id = warehouse.id

        await self.repo.flush()

        await self.warehouse_events.asset_moved_to_warehouse(
            asset_id=asset.id,
            actor_id=actor.id,
            warehouse_id=warehouse.id,
            warehouse_name=getattr(warehouse, "name", None),
        )

        return asset.id
