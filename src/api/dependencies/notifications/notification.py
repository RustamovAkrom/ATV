# api/dependencies/notifications/notification.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.notifications.channels.db_channel import DBChannel
from core.notifications.channels.ws_channel import WebSocketChannel
from core.notifications.dispatcher import NotificationDispatcher
from core.notifications.router import NotificationRouter
from core.notifications.ws.backends.memory import InMemoryWSBackend
from core.notifications.ws.backends.redis import RedisWSBackend
from core.redis import redis_client
from db.dependencies import get_db_session
from repositories.notifications.notification_repo import NotificationRepository
from services.notifications.notification_service import NotificationService

_settings = get_settings()
_memory_ws_backend: InMemoryWSBackend | None = None


# ==================== REPOSITORY ====================


def get_notification_repo(
    db: AsyncSession = Depends(get_db_session),
) -> NotificationRepository:
    """Get notification repository."""
    return NotificationRepository(db)


# ==================== SERVICE ====================


def get_notification_service(
    repo: NotificationRepository = Depends(get_notification_repo),
) -> NotificationService:
    """Get notification service."""
    return NotificationService(repo)


# ==================== WEBSOCKET BACKEND ====================


def get_redis_client():
    """Get Redis client for WebSocket."""
    return redis_client


def get_ws_backend(redis=Depends(get_redis_client)):
    """Get WebSocket backend (memory for dev, Redis for prod)."""
    global _memory_ws_backend

    if _settings.ENV == "prod":
        return RedisWSBackend(redis)

    if _memory_ws_backend is None:
        _memory_ws_backend = InMemoryWSBackend()
    return _memory_ws_backend


def get_ws_memory_backend():
    """Get WebSocket memory backend (alias for compatibility)."""
    return get_ws_backend()


# ==================== DISPATCHER ====================


def get_notification_dispatcher(
    notification_service: NotificationService = Depends(get_notification_service),
    ws_backend=Depends(get_ws_backend),
) -> NotificationDispatcher:
    """Get notification dispatcher with all channels."""
    db_channel = DBChannel(notification_service)
    ws_channel = WebSocketChannel(ws_backend)

    return NotificationDispatcher(
        channels=[db_channel, ws_channel],
    )


# ==================== REDIS LISTENER ====================


def get_redis_listener(
    redis=Depends(get_redis_client),
    memory_backend=Depends(get_ws_memory_backend),
):
    """Get Redis listener for WebSocket events."""
    from core.notifications.ws.redis_listener import RedisListener

    return RedisListener(redis, memory_backend=memory_backend)


# ==================== ROUTER (опционально) ====================


def get_notification_router(
    dispatcher: NotificationDispatcher = Depends(get_notification_dispatcher),
) -> NotificationRouter:
    """Get notification router."""
    return NotificationRouter(channels=dispatcher.channels)
