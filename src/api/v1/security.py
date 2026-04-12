from fastapi import APIRouter, Depends
from pydantic import BaseModel

from services.security_service import SecurityService
from api.dependencies import get_security_service


router = APIRouter(prefix="/security", tags=["Security"])

class ForgotPasswordRequest(BaseModel):
    login: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordRequest,
    service: SecurityService = Depends(get_security_service),
):
    token = await service.request_password_reset(data.login)
    return {"token": token} # TODO: in production change


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    service: SecurityService = Depends(get_security_service),
):
    await service.reset_password(data.token, data.new_password)
    return {"status": "ok"}
