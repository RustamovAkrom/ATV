from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.dependencies import get_db_session

from services.notifications.notification_service import NotificationService
from repositories.notifications.notification_repo import NotificationRepository

from core.notifications.dispatcher import NotificationDispatcher


def get_notification_dispatcher(service: NotificationService = Depends(...)):
    return NotificationDispatcher(service)


def get_notification_repo(
    db: AsyncSession = Depends(get_db_session)
) -> NotificationRepository:
    return NotificationRepository(db)


def get_notification_service(
    repo: NotificationRepository = Depends(get_notification_repo)
) -> NotificationService:
    return NotificationService(repo)
