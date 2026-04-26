from uuid import UUID

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.notifications.notification import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def list_by_user(
        self,
        user_id: UUID,
        is_read: bool | None,
        limit: int,
        offset: int,
    ):
        query = select(Notification).where(Notification.user_id == user_id)

        if is_read is not None:
            query = query.where(Notification.is_read == is_read)

        query = query.order_by(Notification.created_at.desc())

        result = await self.session.execute(
            query.order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def get_by_id(self, notification_id: UUID):
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def mark_as_read(self, notification_id: UUID):
        await self.session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(is_read=True)
        )

    async def mark_all_read(self, user_id: UUID):
        await self.session.execute(
            update(Notification)
            .where(Notification.user_id == user_id)
            .values(is_read=True)
        )

    async def count_unread(self, user_id: UUID):
        result = await self.session.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
            .where(Notification.is_read.is_(False))
        )
        return result.scalar_one()
