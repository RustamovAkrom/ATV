from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from db.models.refresh_token import RefreshToken


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        """
        Create access token
        """

        self.session.add(token)
        await self.session.flush()
        return token

    async def get_by_id(self, jti: UUID) -> RefreshToken | None:
        """
        Get token by jti(UUID) user
        """

        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.id == jti)
        )
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: UUID) -> list[RefreshToken]:
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.created_at.desc())
        )
        return result.scalars().all()

    async def revoke(self, jti: UUID) -> None:
        """
        Revoke one token (logout)
        """

        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.id == jti)
            .values(is_revoked=True)
        )

    async def revoke_all_by_user(self, user_id: UUID) -> None:
        """
        Revoke all user tokens (logout all devices)
        """

        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )

    async def delete_expired(self) -> int:
        """
        Delete expired tokens (cleanup job)
        """

        result = await self.session.execute(
            delete(RefreshToken)
            .where(RefreshToken.expires_at < datetime.now(timezone.utc))
        )
        return result.rowcount or 0
