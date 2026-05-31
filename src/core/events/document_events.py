# core/events/document_events.py
from uuid import UUID

from core.events.domain_event_service import DomainEventService
from core.notifications.builder import NotificationBuilder


class DocumentEventService(DomainEventService):
    """Document domain events."""

    async def attached(
        self,
        *,
        asset_id: UUID,
        document_id: UUID,
        actor_id: UUID,
        asset_name: str,
    ):
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="document_attached",
            description=f"Document {document_id} attached to {asset_name}",
            audit_event="asset.document_attached",
            audit_payload={
                "asset_id": str(asset_id),
                "document_id": str(document_id),
                "actor_id": str(actor_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.document_attached(
                    user_id=actor_id,
                    asset_id=asset_id,
                    document_id=document_id,
                )
            ),
        )

    async def deleted(
        self,
        *,
        asset_id: UUID,
        document_id: UUID,
        actor_id: UUID,
    ):
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="document_deleted",
            description=f"Document {document_id} deleted",
            audit_event="asset.document_deleted",
            audit_payload={
                "asset_id": str(asset_id),
                "document_id": str(document_id),
                "actor_id": str(actor_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.document_deleted(
                    user_id=actor_id,
                    asset_id=asset_id,
                    document_id=document_id,
                )
            ),
        )

    async def updated(
        self,
        *,
        asset_id: UUID,
        document_id: UUID,
        actor_id: UUID,
    ):
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="document_updated",
            description=f"Document {document_id} updated",
            audit_event="asset.document_updated",
            audit_payload={
                "asset_id": str(asset_id),
                "document_id": str(document_id),
                "actor_id": str(actor_id),
            },
            notification=None,
        )
