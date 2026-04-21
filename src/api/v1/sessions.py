from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.dependencies.sessions import get_session_service
from core.exceptions.errors import PermissionDenied
from core.security.auth.dependencies import get_current_user
from db.models.enums import UserRole
from schemas.auth_schema import CurrentUserSchema
from schemas.sessions_schema import SessionOutSchema
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=list[SessionOutSchema])
async def list_sessions(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.list_user_sessions(current_user.id)


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
async def revoke_session(
    session_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    await service.revoke_session(current_user.id, session_id)
    return {"status": "Session revoked"}


@router.post("/logout-all", status_code=status.HTTP_200_OK)
async def logout_all(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    await service.revoke_all(current_user.id)
    return {"detail": "All sessions revoked"}


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_sessions(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    if not current_user.role == UserRole.SUPERADMIN.value:
        raise PermissionDenied()

    deleted = await service.cleanup_expired()
    return {"deleted": deleted}
