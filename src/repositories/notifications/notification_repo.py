from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.notifications.notification import Notification
from repositories.base import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: Notification) -> Notification:
        self.add(notification)
        await self.flush()
        await self.refresh(notification)
        return notification

    async def list_by_user(
        self,
        user_id: UUID,
        is_read: bool | None,
        limit: int,
        offset: int,
    ) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)

        if is_read is not None:
            query = query.where(Notification.is_read == is_read)

        query = query.order_by(Notification.created_at.desc())

        return await self.scalars(
            query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        )

    async def get_by_id(self, notification_id: UUID) -> Notification:
        return await self.scalar(
            select(Notification).where(Notification.id == notification_id)
        )

    async def mark_as_read(self, notification_id: UUID) -> None:
        await self.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(is_read=True)
        )

    async def mark_all_read(self, user_id: UUID) -> None:
        await self.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .values(is_read=True)
        )

    async def count_unread(self, user_id: UUID) -> None | Notification:
        return await self.scalar_one(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read.is_(False))
        )
