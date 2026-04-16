from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from core.security.auth.dependencies import get_current_user
from core.security.auth.types import CurrentUser
from services.session_service import SessionService
from api.dependencies.sessions import get_session_service
from schemas.sessions import SessionOut


router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/", response_model=list[SessionOut])
async def list_sessions(
    current_user: CurrentUser = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.list_user_sessions(current_user.id)


@router.delete("/{session_id}")
async def revoke_session(
    request: Request,
    session_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):

    current_session_id = request.state.session_id

    if str(session_id) == str(current_session_id):
        raise HTTPException(
            status_code=400,
            detail="Cannot revoke current session",
        )

    await service.revoke_session(current_user.id, session_id)

    return {"status": "revoked"}


@router.post("/logout-all")
async def logout_all(
    current_user: CurrentUser = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    await service.revoke_all(current_user.id)
    return {"status": "revoked_all"}


@router.post("/cleanup")
async def cleanup_sessions(
    service: SessionService = Depends(get_session_service),
):
    deleted = await service.cleanup_expired()
    return {"deleted": deleted}
