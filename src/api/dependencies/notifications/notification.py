from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.notifications.channels.db_channel import DBChannel
from core.notifications.channels.websocket import WebSocketManager
from core.notifications.channels.ws_channel import WebSocketChannel
from core.notifications.router import NotificationRouter
from db.dependencies import get_db_session

from services.notifications.notification_service import NotificationService
from repositories.notifications.notification_repo import NotificationRepository

from core.notifications.dispatcher import NotificationDispatcher
from core.config import get_settings


def get_notification_repo(
    db: AsyncSession = Depends(get_db_session),
) -> NotificationRepository:
    return NotificationRepository(db)


def get_notification_service(
    repo: NotificationRepository = Depends(get_notification_repo),
) -> NotificationService:
    return NotificationService(repo)


def get_notification_dispatcher(
    service: NotificationService = Depends(get_notification_service),
) -> NotificationDispatcher:
    return NotificationDispatcher(service)


def get_redis_client():
    from core.redis import redis_client

    return redis_client


def get_ws_backend(redis=Depends(get_redis_client)):
    settings = get_settings()

    if settings.ENV == "prod":
        from core.notifications.ws.backends.redis import RedisWSBackend

        return RedisWSBackend(redis)

    from core.notifications.ws.backends.memory import InMemoryWSBackend

    return InMemoryWSBackend()


def get_notification_dispatcher(
    notification_service=Depends(get_notification_service),
    ws_backend=Depends(get_ws_backend),
):
    from core.notifications.channels.db_channel import DBChannel
    from core.notifications.channels.ws_channel import WebSocketChannel

    db_channel = DBChannel(notification_service)
    ws_channel = WebSocketChannel(ws_backend)

    return NotificationDispatcher(
        channels=[db_channel, ws_channel],
    )


def get_ws_memory_backend():
    from core.notifications.ws.backends.memory import InMemoryWSBackend

    return InMemoryWSBackend()


def get_redis_listener(redis=Depends(get_redis_client)):
    from core.notifications.ws.redis_listener import RedisListener

    return RedisListener(redis, memory_backend=get_ws_memory_backend())
