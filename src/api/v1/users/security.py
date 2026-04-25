from fastapi import APIRouter, Depends, Request

from api.dependencies.security import get_security_service
from core.slowapi import limiter
from services.security_service import SecurityService
from schemas.security import ForgotPasswordRequest, ResetPasswordRequest

router = APIRouter(prefix="/security", tags=["Security"])


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    service: SecurityService = Depends(get_security_service),
):
    await service.request_password_reset(data.login)
    return {"status": "ok"}


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    service: SecurityService = Depends(get_security_service),
):
    await service.reset_password(data.token, data.new_password)
    return {"status": "ok"}
