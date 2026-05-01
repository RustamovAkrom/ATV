# core/events/document_event_service.py

from uuid import UUID
from core.events.base import BaseEventService
from core.notifications.dispatcher import NotificationDispatcher
from services.assets.asset_history_service import AssetHistoryService
from core.notifications.builder import NotificationBuilder
from core.notifications.types import NotificationType


class DocumentEventService(BaseEventService):

    def __init__(
        self,
        history: AssetHistoryService,
        notifications: NotificationDispatcher,
    ):
        self.history = history
        self.notifications = notifications

    async def attached(
        self,
        asset_id: UUID,
        document_id: UUID,
        actor_id: UUID,
        asset_name: str,
    ):
        await self.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "document_attached",
                f"Document {document_id} attached to {asset_name}",
            ),
            audit_event=NotificationType.DOCUMENT_ATTACHED,
            audit_payload={
                "asset_id": str(asset_id),
                "document_id": str(document_id),
                "actor_id": str(actor_id),
                "asset_name": asset_name,
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
        asset_id: UUID,
        document_id: UUID,
        actor_id: UUID
    ):
        await self.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "document_deleted",
                f"Document {document_id} deleted",
            ),
            audit_event=NotificationType.DOCUMENT_DELETED,
            audit_payload={
                "asset_id": str(asset_id),
                "document_id": str(document_id),
                "actor_id": str(actor_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder._base(
                    user_id=actor_id,
                    type=NotificationType.DOCUMENT_DELETED,
                    title="Document Deleted",
                    message=f"You deleted a document from the asset",
                    data={
                        "asset_id": str(asset_id),
                        "document_id": str(document_id),
                    },
                )
            ),
        )
