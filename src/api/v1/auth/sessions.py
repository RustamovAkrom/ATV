from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from api.dependencies.sessions import get_session_service
from core.cache.decorators import cached, invalidate_cache
from core.exceptions.errors import PermissionDenied
from core.security.auth.dependencies import get_current_user
from core.slowapi import limiter
from db.models.enums import UserRole
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from schemas.users.sessions import CleanupResponseSchema, SessionOutSchema
from services.users.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=list[SessionOutSchema])
@cached(tags=("sessions:list",))
async def list_sessions(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.list_user_sessions(current_user.id)


@router.delete(
    "/{session_id}", response_model=StatusResponse, status_code=status.HTTP_200_OK
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("sessions:list",))
async def revoke_session(
    request: Request,
    session_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    await service.revoke_session(current_user.id, session_id)
    return StatusResponse(status="ok", message="Session revoked")


@router.post("/logout-all", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
@invalidate_cache(tags=("sessions:list",))
async def logout_all(
    request: Request,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    await service.revoke_all(current_user.id)
    return StatusResponse(status="ok", message="All sessions revoked successfully")


@router.post(
    "/cleanup", response_model=CleanupResponseSchema, status_code=status.HTTP_200_OK
)
@limiter.limit("20/minute")
@invalidate_cache(tags=("sessions:list",))
async def cleanup_sessions(
    request: Request,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    if not current_user.role == UserRole.SUPERADMIN.value:
        raise PermissionDenied()

    deleted = await service.cleanup_expired()
    return CleanupResponseSchema(deleted=deleted)
