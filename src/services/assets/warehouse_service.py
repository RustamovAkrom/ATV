from uuid import UUID

from core.audit.stream import audit_stream
from core.exceptions.errors import BadRequest, NotFound
from repositories.warehouse.warehouse_repo import WarehouseRepository
from schemas.assets.warehouses import WarehouseMoveRequest
from utils.helpers import utc_now
from schemas.auth.auth import CurrentUserSchema

class WarehouseService:
    def __init__(self, repo: WarehouseRepository):
        self.repo = repo

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
        await self.repo.add_history(
            asset.id,
            actor.id,
            "warehouse_moved",
            f"Asset moved to warehouse {warehouse.id}",
        )
        await self._publish(
            "asset.warehouse_moved",
            {
                "asset_id": str(asset.id),
                "warehouse_id": str(warehouse.id),
                "actor_id": str(actor.id),
            },
        )
        return warehouse.id

    async def _publish(self, event: str, payload: dict) -> None:
        try:
            await audit_stream.publish(
                {"event": event, **payload, "timestamp": utc_now().timestamp()}
            )
        except Exception:
            return
