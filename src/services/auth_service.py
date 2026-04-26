from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import Request
from jwt import PyJWTError

from core.config import get_settings
from core.exceptions.errors import AuthenticationError, InvalidToken
from core.security.blacklist import get_blacklist
from core.security.jwt import create_access_token, create_refresh_token, decode_token
from core.security.passwords import verify_password
from db.models.refresh_token import RefreshToken
from db.models.users.user import User
from repositories.auth_repo import AuthRepository
from repositories.user_repo import UserRepository
from schemas.auth import TokenPairSchema
from utils.helpers import generate_device_id, utc_now


class AuthService:
    def __init__(self, user_repo: UserRepository, auth_repo: AuthRepository):
        self.settings = get_settings()
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def login(
        self, login: str, password: str, request: Request
    ) -> TokenPairSchema:
        user: User = await self.user_repo.get_by_identity(login)

        if not user:
            raise AuthenticationError()

        # verify hashes
        if not verify_password(password, user.password_hash):
            raise AuthenticationError()

        if not user.is_active:
            raise AuthenticationError()

        refresh, jti = create_refresh_token(str(user.id))
        access = create_access_token(str(user.id), str(jti))

        user.last_login = utc_now()

        await self.auth_repo.create(
            RefreshToken(
                id=UUID(jti),
                user_id=user.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                device_id=generate_device_id(request),
                expires_at=utc_now()
                + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            )
        )

        return TokenPairSchema(
            access_token=access,
            refresh_token=refresh,
        )

    async def refresh(self, refresh_token: str, request: Request) -> TokenPairSchema:
        payload = await decode_token(refresh_token, "refresh")

        token = await self.auth_repo.get_by_id(payload.jti)
        if not token:
            raise InvalidToken()

        # reuse detection (security event)
        if token.is_revoked:
            await self.auth_repo.revoke_all_by_user(payload.sub)
            raise InvalidToken("Token reuse detected")

        # expired
        if token.expires_at < utc_now():
            raise InvalidToken()

        current_ip = request.client.host if request.client else None
        current_device = generate_device_id(request)

        # DEVICE binding (new)
        if token.device_id and token.device_id != current_device:
            await self.auth_repo.revoke_all_by_user(payload.sub)
            raise InvalidToken("Device mismatch detected")

        # IP binding (optional but good)
        if token.ip_address and token.ip_address != current_ip:
            await self.auth_repo.revoke_all_by_user(payload.sub)
            raise InvalidToken("IP mismatched")

        user = await self.user_repo.get_by_id(payload.sub)
        if not user:
            raise InvalidToken()

        if user.last_password_change and payload.iat:
            if payload.iat <= int(user.last_password_change.timestamp()):
                await self.auth_repo.revoke_all_by_user(user.id)
                raise InvalidToken("Token outdated")

        await self.auth_repo.revoke(payload.jti)

        new_refresh, new_jti = create_refresh_token(str(user.id))
        access = create_access_token(str(user.id), str(new_jti))

        await self.auth_repo.create(
            RefreshToken(
                id=UUID(new_jti),
                user_id=user.id,
                ip_address=current_ip,
                user_agent=request.headers.get("user-agent"),
                device_id=current_device,
                expires_at=utc_now()
                + timedelta(days=self.settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            )
        )

        return TokenPairSchema(
            access_token=access,
            refresh_token=new_refresh,
        )

    async def logout(self, request: Request, refresh_token: str) -> None:
        payload = getattr(request.state, "access_payload", None)

        if not payload:
            raise InvalidToken("Missing access payload")

        await get_blacklist().add(
            jti=payload.jti,
            exp=datetime.fromtimestamp(payload.exp, tz=UTC),
        )

        try:
            refresh_payload = await decode_token(refresh_token, "refresh")
            await self.auth_repo.revoke(refresh_payload.jti)
        except (InvalidToken, PyJWTError, ValueError, TypeError):
            pass  # logout всегда успешен

    async def logout_all(self, request: Request, user_id: UUID) -> None:
        payload = getattr(request.state, "access_payload", None)

        if payload:
            await get_blacklist().add(
                jti=payload.jti,
                exp=datetime.fromtimestamp(payload.exp, tz=UTC),
            )

        await self.auth_repo.revoke_all_by_user(user_id)
