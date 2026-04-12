from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from repositories.auth_repo import AuthRepository
from repositories.user_repo import UserRepository
from db.models.refresh_token import RefreshToken
from core.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from core.security.passwords import verify_password
from core.config import get_settings
from core.security.blacklist import get_blacklist
from core.exceptions.errors import (
    AuthenticationError,
    InvalidToken,
)

def utc_now():
    return datetime.now(timezone.utc)

class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_repo: AuthRepository,
    ):
        self.settings = get_settings()
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    # =========================
    # LOGIN
    # =========================
    async def login(self, login: str, password: str) -> dict[str, str]:
        user = await self.user_repo.get_by_login(login)

        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError()

        if not user.is_active:
            raise AuthenticationError()

        user.last_login = utc_now()

        access = create_access_token(str(user.id))
        refresh, jti = create_refresh_token(str(user.id))

        await self.auth_repo.create(
            RefreshToken(
                id=jti,
                user_id=user.id,
                expires_at=utc_now()
                + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            )
        )

        return {
            "access_token": access,
            "refresh_token": refresh,
        }

    # =========================
    # REFRESH
    # =========================
    async def refresh(self, refresh_token: str) -> dict[str, str]:
        payload = await decode_token(refresh_token, expected_type="refresh")

        if payload.get("type") != "refresh":
            raise InvalidToken()

        jti = payload.get("jti")
        user_id = payload.get("sub")

        token = await self.auth_repo.get_by_id(jti)

        if not token:
            raise InvalidToken()

        if token.is_revoked:
            await self.auth_repo.revoke_all_by_user(token.user_id)
            raise InvalidToken(detail="Token reuse detected")

        if token.expires_at < utc_now():
            raise InvalidToken()

        # rotate token
        await self.auth_repo.revoke(jti)

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidToken()

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

        return {
            "access_token": access,
            "refresh_token": new_refresh,
        }

    # =========================
    # LOGOUT
    # =========================
    async def logout(self, refresh_token: str, access_payload: dict[str, Any]) -> None:
        blacklist = get_blacklist()

        jti = access_payload.get("jti")
        exp = access_payload.get("exp")

        # 🔥 безопасная проверка
        if jti and exp:
            await blacklist.add(
                jti=jti,
                exp=datetime.fromtimestamp(exp, tz=timezone.utc),
            )

        payload = await decode_token(refresh_token)

        refresh_jti = payload.get("jti")
        refresh_sub = payload.get("sub")

        if access_payload.get("sub") != refresh_sub:
            raise InvalidToken()

        await self.auth_repo.revoke(refresh_jti)

    # =========================
    # LOGOUT ALL
    # =========================
    async def logout_all(self, user_id: UUID) -> None:
        await self.auth_repo.revoke_all_by_user(user_id)
