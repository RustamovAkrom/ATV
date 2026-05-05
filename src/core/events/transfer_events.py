from uuid import UUID

from core.events.base import BaseEventService
from core.notifications.builder import NotificationBuilder
from core.notifications.dispatcher import NotificationDispatcher
from services.assets.asset_history_service import AssetHistoryService


class TransferEventService:
    def __init__(
        self,
        base: BaseEventService,
        history: AssetHistoryService,
        notifications: NotificationDispatcher,
    ):
        self.base = base
        self.history = history
        self.notifications = notifications

    async def created(self, *, asset_id: UUID, transfer_id: UUID, actor_id: UUID):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "transfer_created",
                f"Transfer {transfer_id} created",
            ),
            audit_event="asset.transfer_created",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "transfer_id": str(transfer_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.asset_transfer_created(
                    user_id=actor_id,
                    asset_id=asset_id,
                    transfer_id=transfer_id,
                )
            ),
        )

    async def approved(
        self,
        *,
        asset_id: UUID,
        transfer_id: UUID,
        actor_id: UUID,
        created_by_id: UUID,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "transfer_approved",
                f"Transfer {transfer_id} approved",
            ),
            audit_event="asset.transfer_approved",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "transfer_id": str(transfer_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.asset_transfer_completed(
                    user_id=created_by_id,
                    asset_id=asset_id,
                )
            ),
        )

    async def rejected(
        self,
        *,
        asset_id: UUID,
        transfer_id: UUID,
        actor_id: UUID,
        created_by_id: UUID,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "transfer_rejected",
                f"Transfer {transfer_id} rejected",
            ),
            audit_event="asset.transfer_rejected",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "transfer_id": str(transfer_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.asset_transfer_rejected(
                    user_id=created_by_id,
                    asset_id=asset_id,
                )
            ),
        )
