# core/events/transfer_events.py
from uuid import UUID

from core.events.domain_event_service import DomainEventService
from core.notifications.builder import NotificationBuilder


class TransferEventService(DomainEventService):
    """Transfer domain events."""

    async def created(self, *, asset_id: UUID, transfer_id: UUID, actor_id: UUID):
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="transfer_created",
            description=f"Transfer {transfer_id} created",
            audit_event="asset.transfer_created",
            audit_payload={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
                "actor_id": str(actor_id),
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
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="transfer_approved",
            description=f"Transfer {transfer_id} approved",
            audit_event="asset.transfer_approved",
            audit_payload={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
                "actor_id": str(actor_id),
                "created_by_id": str(created_by_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.asset_transfer_completed(
                    user_id=created_by_id,
                    asset_id=asset_id,
                    transfer_id=transfer_id,
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
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="transfer_rejected",
            description=f"Transfer {transfer_id} rejected",
            audit_event="asset.transfer_rejected",
            audit_payload={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
                "actor_id": str(actor_id),
                "created_by_id": str(created_by_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.asset_transfer_rejected(
                    user_id=created_by_id,
                    asset_id=asset_id,
                    transfer_id=transfer_id,
                )
            ),
        )
