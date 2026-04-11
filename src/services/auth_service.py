from datetime import datetime, timedelta
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
from core.exceptions.errors import (
    AuthenticationError,
    InvalidToken,
    RateLimitExceeded,
)


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        auth_repo: AuthRepository,
    ):
        self.settings = get_settings()
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def login(self, login: str, password: str) -> dict[str, str]:
        user = await self.user_repo.get_by_login(login)

        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError()

        access = create_access_token(str(user.id))
        refresh, jti = create_refresh_token(str(user.id))

        token = RefreshToken(
            id=UUID(jti),
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        await self.auth_repo.create(token)

        return {
            "access_token": access,
            "refresh_token": refresh
        }

    async def refresh(self, refresh_token: str) -> dict[str, str]:
        payload = await decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise InvalidToken()

        jti_raw = payload.get("jti")
        sub_raw = payload.get("sub")
        if not isinstance(jti_raw, str) or not isinstance(sub_raw, str):
            raise InvalidToken()

        jti = UUID(jti_raw)

        token = await self.auth_repo.get_by_id(jti)

        if not token:
            raise InvalidToken()

        if token.is_revoked:
            await self.auth_repo.revoke_all_by_user(token.user_id)
            raise InvalidToken(detail="Token reuse detected")

        if token.expires_at < datetime.utcnow():
            raise InvalidToken()

        await self.auth_repo.revoke(jti)

        user = await self.user_repo.get_by_id(UUID(sub_raw))
        if not user:
            raise InvalidToken()

        access = create_access_token(str(user.id))
        new_refresh, new_jti = create_refresh_token(str(user.id))

        await self.auth_repo.create(
            RefreshToken(
                id=UUID(new_jti),
                user_id=user.id,
                expires_at=datetime.utcnow() + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            )
        )
        return {
            "access_token": access,
            "refresh_token": new_refresh
        }

    async def logout(self, refresh_token: str, access_payload: dict[str, Any]) -> None:

        # # blacklist access token
        # await add_to_blacklist(
        #     jti=access_payload['jti'],
        #     exp=datetime.fromtimestamp(access_payload['exp'], tz=timezone.utc),
        # )

        # revoke refresh
        payload = await decode_token(refresh_token)
        jti_raw = payload.get("jti")
        sub_raw = payload.get("sub")
        if not isinstance(jti_raw, str) or not isinstance(sub_raw, str):
            raise InvalidToken()

        # Ensure user can only revoke own refresh token.
        if access_payload.get("sub") != sub_raw:
            raise InvalidToken()

        await self.auth_repo.revoke(UUID(jti_raw))

    async def logout_all(self, user_id: UUID) -> None:
        await self.auth_repo.revoke_all_by_user(user_id)
