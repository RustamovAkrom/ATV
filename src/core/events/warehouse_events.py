# core/events/warehouse_events.py
from uuid import UUID

from core.events.domain_event_service import DomainEventService
from core.notifications.builder import NotificationBuilder


class WarehouseEventService(DomainEventService):
    """Warehouse domain events."""

    async def asset_moved_to_warehouse(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        warehouse_id: UUID,
        warehouse_name: str | None = None,
    ):
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="moved_to_warehouse",
            description=f"Moved to warehouse {warehouse_name or warehouse_id}",
            audit_event="asset.moved_to_warehouse",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "warehouse_id": str(warehouse_id),
                "warehouse_name": warehouse_name,
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.asset_moved_to_warehouse(
                    user_id=actor_id,
                    asset_id=asset_id,
                    warehouse_id=warehouse_id,
                    warehouse_name=warehouse_name,
                )
            ),
        )
