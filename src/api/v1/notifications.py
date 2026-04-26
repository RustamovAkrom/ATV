from uuid import UUID

from fastapi import APIRouter, Depends

from core.security.auth.dependencies import get_current_user
from schemas.auth import CurrentUserSchema
from schemas.notifications.notification import NotificationSchema
from services.notifications.notification_service import NotificationService
from api.dependencies.notifications import get_notification_service

router = APIRouter(prefix="/notifications", tags=["Notifications"])


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
