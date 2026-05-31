import asyncio
from contextlib import suppress
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from api.dependencies.notifications.notification import (
    get_notification_service,
    get_redis_listener,
    get_ws_memory_backend,
)
from core.notifications.channels.websocket import WebSocketManager
from core.notifications.ws.redis_listener import RedisListener
from core.security.auth.dependencies import get_current_user
from core.security.auth.ws_dependencies import get_current_user_ws
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from schemas.notifications.notification import (
    NotificationSchema,
    UnreadCountResponseSchema,
)
from schemas.pagination import PaginationParamsSchema
from services.notifications.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.websocket("/ws/notifications")
async def ws_notifications(
    websocket: WebSocket,
    current_user: CurrentUserSchema = Depends(get_current_user_ws),
    memory_backend: WebSocketManager = Depends(get_ws_memory_backend),
    redis_listener: RedisListener = Depends(get_redis_listener),
):
    user_id = current_user.id

    await memory_backend.connect(user_id, websocket)

    task = None

    if redis_listener:
        task = asyncio.create_task(redis_listener.listen_user(user_id))

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        memory_backend.disconnect(user_id, websocket)

    except Exception:
        memory_backend.disconnect(user_id, websocket)
        raise

    finally:
        if task:
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task


@router.get("/", response_model=list[NotificationSchema])
async def get_notifications(
    is_read: bool | None = None,
    pagination: PaginationParamsSchema = Depends(),
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list_by_user(
        user_id=current_user.id, is_read=is_read, pagination=pagination
    )


@router.post("/{notification_id}/read", response_model=StatusResponse)
async def mark_as_read(
    notification_id: UUID,
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    await service.mark_as_read(
        notification_id=notification_id,
        actor_id=current_user.id,
    )
    return StatusResponse(status="ok", message="Notification marked as read")


@router.post("/read-all", response_model=StatusResponse)
async def mark_all_as_read(
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    await service.mark_all_as_read(actor_id=current_user.id)
    return StatusResponse(status="ok", message="All notifications marked as read")


@router.get("/unread-count", response_model=UnreadCountResponseSchema)
async def unread_count(
    service: NotificationService = Depends(get_notification_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    count = await service.get_unread_count(actor_id=current_user.id)
    return UnreadCountResponseSchema(count=count)
