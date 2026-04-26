from uuid import UUID

from core.exceptions.errors import NotFound, PermissionDenied
from db.models.notifications.notification import Notification
from repositories.notifications.notification_repo import NotificationRepository
from schemas.notifications.notification import NotificationSchema
from utils.helpers import utc_now


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def create(
        self,
        user_id: UUID,
        type: str,
        title: str,
        message: str,
        data: dict | None = None,
    ) -> NotificationSchema:

        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            data=data or {},
        )

        await self.repo.create(notification)

        return NotificationSchema.model_validate(notification)

    async def list_by_user(
        self,
        user_id: UUID,
        is_read: bool | None,
        limit: int,
        offset: int,
    ):
        items = await self.repo.list_by_user(user_id, is_read, limit, offset)

        return [NotificationSchema.model_validate(i) for i in items]

    async def mark_as_read(self, notification_id: UUID, actor_id: UUID):
        notification = await self.repo.get_by_id(notification_id)

        if not notification:
            raise NotFound("Notification not found")

        if notification.user_id != actor_id:
            raise PermissionDenied("Access denied")

        notification.is_read = True
        notification.read_at = utc_now()

        await self.repo.session.flush()

    async def mark_all_as_read(self, actor_id: UUID):
        await self.repo.mark_all_read(actor_id)

    async def get_unread_count(self, actor_id: UUID) -> int:
        return await self.repo.count_unread(actor_id)
