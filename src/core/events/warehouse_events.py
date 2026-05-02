from uuid import UUID

from core.events.base import BaseEventService
from core.notifications.builder import NotificationBuilder
from core.notifications.dispatcher import NotificationDispatcher
from services.assets.asset_history_service import AssetHistoryService


class WarehouseEventService:
    def __init__(
        self,
        base: BaseEventService,
        history: AssetHistoryService,
        notifications: NotificationDispatcher,
    ):
        super().__init__()
        self.base = base
        self.history = history
        self.notifications = notifications

    async def asset_moved_to_warehouse(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        warehouse_id: UUID,
        warehouse_name: str | None = None,
    ):
        await self.base.execute(
            # History
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "moved_to_warehouse",
                f"Moved to warehouse {warehouse_name or warehouse_id}",
            ),
            # Audit
            audit_event="asset.moved_to_warehouse",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "warehouse_id": str(warehouse_id),
                "warehouse_name": warehouse_name,
            },
            # Notification
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder._base(
                    user_id=actor_id,
                    type="asset.moved_to_warehouse",
                    title="Asset moved to warehouse",
                    message=f"Asset moved to warehouse {warehouse_name or ''}",
                    data={
                        "asset_id": str(asset_id),
                        "warehouse_id": str(warehouse_id),
                    },
                )
            )
        )
