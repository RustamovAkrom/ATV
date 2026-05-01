from uuid import UUID
import asyncio

from fastapi import APIRouter, WebSocket, Depends

from core.security.auth.dependencies import get_current_user
from schemas.auth import CurrentUserSchema
from schemas.notifications.notification import NotificationSchema
from services.notifications.notification_service import NotificationService

from core.security.auth.ws_dependencies import get_current_user_ws
from core.notifications.channels.websocket import WebSocketManager, get_ws_manager
from api.dependencies.notifications.notification import (
    get_notification_service,
    get_redis_listener,
    get_ws_memory_backend,
)
from core.notifications.ws.redis_listener import RedisListener


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.websocket("/ws/notifications")
async def ws_notifications(
    websocket: WebSocket,
    user: CurrentUserSchema = Depends(get_current_user_ws),
    memory_backend: WebSocketManager = Depends(get_ws_memory_backend),
    redis_listener: RedisListener = Depends(get_redis_listener),
):
    user_id = user.id

    await memory_backend.connect(user_id, websocket)

    if redis_listener:
        task = asyncio.create_task(redis_listener.listen_user(user_id))

    try:
        while True:
            await websocket.receive_text()
    except:
        memory_backend.disconnect(user_id, websocket)


@router.get("/", response_model=list[NotificationSchema])
async def get_notifications(
    is_read: bool | None = None,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list_by_user(
        user_id=current_user.id,
        is_read=is_read,
        limit=50,
        offset=0,
    )


@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    await service.mark_as_read(notification_id, current_user.id)
    return {"status": "ok"}


@router.post("/read-all")
async def mark_all_as_read(
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    await service.mark_all_as_read(current_user.id)
    return {"status": "ok"}


@router.get("/unread-count")
async def unread_count(
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    count = await service.get_unread_count(current_user.id)
    return {"count": count}
