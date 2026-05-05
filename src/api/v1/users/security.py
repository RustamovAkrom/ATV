from fastapi import APIRouter, Depends, Request, status

from api.dependencies.auth.security import get_security_service
from core.slowapi import limiter
from schemas.common import StatusResponse
from schemas.auth.security import (
    ForgotPasswordRequestSchema,
    ResetPasswordRequestSchema,
)
from services.auth.security_service import SecurityService

router = APIRouter(prefix="/security", tags=["Security"])


@router.post(
    "/forgot-password", response_model=StatusResponse, status_code=status.HTTP_200_OK
)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequestSchema,
    service: SecurityService = Depends(get_security_service),
):
    """
    Request to recover the password.
    Sends a link with a token to the user's email.
    """
    await service.request_password_reset(data.login)
    return StatusResponse(
        status="ok", message="If the acccount exists, a reset link has been sent."
    )


@router.post(
    "/reset-password", response_model=StatusResponse, status_code=status.HTTP_200_OK
)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    data: ResetPasswordRequestSchema,
    service: SecurityService = Depends(get_security_service),
):
    """
    Set a new password using the token from the email.
    """
    await service.reset_password(data.token, data.new_password)
    return StatusResponse(status="ok", message="Password has been reset successfully")
