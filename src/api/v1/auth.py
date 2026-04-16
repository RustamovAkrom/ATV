from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from core.security.auth.dependencies import get_current_user
from core.security.auth.types import CurrentUser
from core.slowapi import limiter
from services.auth_service import AuthService
from api.dependencies.auth import get_auth_service
from schemas.auth import RefreshRequest, TokenResponse
from core.config import get_settings

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()
MAX_AGE = 60 * 15 # TTL access token

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    tokens = await service.login(
        form_data.username,
        form_data.password,
        request,
    )

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=MAX_AGE,
    )

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    tokens = await service.refresh(data.refresh_token, request)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=not settings.DEBUG,
        samesite="lax",
        max_age=MAX_AGE,
    )

    return tokens


@router.post("/logout")
async def logout(
    request: Request,
    data: RefreshRequest,
    response: Response,
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(request, data.refresh_token)

    response.delete_cookie("access_token")

    return {"status": "ok"}


@router.post("/logout-all")
async def logout_all(
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.logout_all(current_user.id)
    return {"status": "ok"}
