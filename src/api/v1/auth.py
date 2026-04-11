from fastapi import APIRouter, Depends, Request, Response
from uuid import UUID

from schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from services.auth_service import AuthService
from api.dependencies import get_auth_service
from core.config import get_settings
from core.security.dependencies import get_current_user
from core.security.types import CurrentUser
from core.slowapi import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()


@router.post(
    "/login",
    response_model=TokenResponse,
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    tokens = await service.login(data.login, data.password)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.ENV not in ("local", "dev", "test"),
        samesite="strict",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES * 60,
        path="/",
    )

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    tokens = await service.refresh(data.refresh_token)
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.ENV not in ("local", "dev", "test"),
        samesite="strict",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES * 60,
        path="/",
    )
    return tokens


@router.post("/logout")
async def logout(
    data: RefreshRequest,
    response: Response,
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await service.logout(data.refresh_token, current_user)
    response.delete_cookie(
        "access_token",
        path="/",
        secure=settings.ENV not in ("local", "dev", "test"),
        samesite="strict",
    )
    return {"status": "ok"}


@router.post("/logout-all")
async def logout_all(
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    await service.logout_all(UUID(current_user["sub"]))
    return {"status": "ok"}


@router.get("/me")
async def me(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    return current_user
