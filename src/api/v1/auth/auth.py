from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies.auth.auth import get_auth_service
from core.config import get_settings
from core.security.auth.dependencies import get_current_user
from core.slowapi import limiter
from schemas.auth import CurrentUserSchema, RefreshRequestSchema, TokenResponseSchema
from services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()
MAX_AGE = settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES * 60


@router.post("/login", response_model=TokenResponseSchema)
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
        value=tokens.access_token,
        httponly=True,
        secure=not settings.DEBUG and settings.ENV == "prod",
        samesite="lax",
        max_age=MAX_AGE,
        path="/",
    )

    return tokens


@router.post("/refresh", response_model=TokenResponseSchema)
async def refresh(
    data: RefreshRequestSchema,
    request: Request,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    tokens = await service.refresh(data.refresh_token, request)

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=not settings.DEBUG and settings.ENV == "prod",
        samesite="lax",
        max_age=MAX_AGE,
        path="/",
    )

    return tokens


@router.post("/logout")
async def logout(
    request: Request,
    data: RefreshRequestSchema,
    response: Response,
    _: CurrentUserSchema = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.logout(request, data.refresh_token)

    response.delete_cookie("access_token", path="/")

    return {"status": "ok"}


@router.post("/logout-all")
async def logout_all(
    request: Request,
    response: Response,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    await service.logout_all(request, current_user.id)
    response.delete_cookie("access_token", path="/")
    return {"status": "ok"}
