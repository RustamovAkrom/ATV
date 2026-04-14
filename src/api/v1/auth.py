from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from core.security.auth.dependencies import get_current_user
from src.core.security.auth.types import CurrentUser
from services.auth_service import AuthService
from api.dependencies.auth import get_auth_service
from schemas.auth import RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    """
    Login: username or password
    password: xxxxxxxxx
    """

    tokens = await service.login(
        form_data.username,
        form_data.password,
        request,
    )

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="lax",
    )

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    response: Response,
    service: AuthService = Depends(get_auth_service),
):
    """
    Create new access and refresh tokens with your refresh token
    """

    tokens = await service.refresh(data.refresh_token)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        samesite="lax",
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
    """
    Logout delete access token from cookies
    """

    await service.logout(request, data.refresh_token)

    response.delete_cookie("access_token")

    return {"status": "ok"}


@router.post("/logout-all")
async def logout_all(
    current_user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """
    Logout from all devices
    """

    await service.logout_all(current_user.id)
    return {"status": "ok"}
