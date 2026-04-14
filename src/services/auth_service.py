from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import Request

from core.config import get_settings
from core.exceptions.errors import AuthenticationError, InvalidToken
from core.security.blacklist import get_blacklist
from core.security.jwt import create_access_token, create_refresh_token, decode_token
from core.security.passwords import verify_password
from db.models.refresh_token import RefreshToken
from repositories.user_repo import UserRepository
from repositories.auth_repo import AuthRepository

def utc_now():
    return datetime.now(timezone.utc)


class AuthService:
    def __init__(self, user_repo: UserRepository, auth_repo: AuthRepository):
        self.settings = get_settings()
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def login(self, login: str, password: str, request: Request):
        user = await self.user_repo.get_by_identity(login)

        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError()

        if not user.is_active:
            raise AuthenticationError()

        access = create_access_token(str(user.id))
        refresh, jti = create_refresh_token(str(user.id))

        await self.auth_repo.create(
            RefreshToken(
                id=jti,
                user_id=user.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                expires_at=utc_now()
                + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            )
        )

        return {"access_token": access, "refresh_token": refresh}

    async def refresh(self, refresh_token: str):
        payload = await decode_token(refresh_token, "refresh")

        token = await self.auth_repo.get_by_id(payload.jti)

        if not token or token.is_revoked:
            raise InvalidToken()

        await self.auth_repo.revoke(payload.jti)

        user = await self.user_repo.get_by_id(payload.sub)

        access = create_access_token(str(user.id))
        new_refresh, new_jti = create_refresh_token(str(user.id))

        await self.auth_repo.create(
            RefreshToken(
                id=new_jti,
                user_id=user.id,
                expires_at=utc_now()
                + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            )
        )

        return {"access_token": access, "refresh_token": new_refresh}

    async def logout(self, request: Request, refresh_token: str):
        payload = request.state.access_payload

        await get_blacklist().add(
            jti=payload.jti,
            exp=datetime.fromtimestamp(payload.exp, tz=timezone.utc),
        )

        try:
            refresh_payload = await decode_token(refresh_token, "refresh")
            await self.auth_repo.revoke(refresh_payload.jti)
        except Exception:
            pass  # logout всегда успешен

    async def logout_all(self, user_id: UUID):
        await self.auth_repo.revoke_all_by_user(user_id)
