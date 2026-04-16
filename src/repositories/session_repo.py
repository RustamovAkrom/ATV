from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.refresh_token import RefreshToken
from utils.helpers import utc_now


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_sessions(self, user_id: UUID):
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.created_at.desc())
        )
        return result.scalars().all()

    async def get_active_sessions(self, user_id: UUID):
        now = utc_now()

        result = await self.session.execute(
            select(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > now,
            )
        )
        return result.scalars().all()

    async def get_by_id(self, session_id: UUID):
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.id == session_id)
        )
        return result.scalar_one_or_none()

    async def revoke(self, session_id: UUID):
        await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.id == session_id,
                RefreshToken.is_revoked == False,
            )
            .values(is_revoked=True)
        )

    async def revoke_all(self, user_id: UUID):
        await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
            )
            .values(is_revoked=True)
        )
