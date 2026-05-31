from typing import Any
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.refresh_token import RefreshToken
from repositories.base import BaseRepository
from utils.helpers import utc_now


class SessionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_sessions(self, user_id: UUID):
        now = utc_now()

        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .order_by(RefreshToken.created_at.desc())
        )

        sessions = result.scalars().all()

        return [s for s in sessions if s.expires_at > now]

    async def get_by_id(self, session_id: UUID):
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.id == session_id)
        )
        return result.scalar_one_or_none()

    async def revoke(self, session_id: UUID) -> bool:
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.id == session_id,
                RefreshToken.is_revoked.is_(False),
            )
            .values(is_revoked=True)
        )
        return self._rowcount(result) > 0

    async def revoke_all(self, user_id: UUID) -> int:
        result = await self.session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked.is_(False),
            )
            .values(is_revoked=True)
        )
        return self._rowcount(result)

    async def get_active_sessions(self, user_id: UUID):
        now = utc_now()

        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked.is_(False),
                RefreshToken.expires_at > now,
            )
        )
        return list(result.scalars().all())

    async def delete_expired_sessions(self) -> int:
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < utc_now())
        )
        return self._rowcount(result)

    async def delete_expired_sessions_sync(self) -> int:
        result = await self.session.execute(
            delete(RefreshToken).where(RefreshToken.expires_at < utc_now())
        )
        await self.session.commit()

        return self._rowcount(result)

    def _to_schema(self, session: RefreshToken) -> dict[str, Any]:
        now = utc_now()

        return {
            "id": session.id,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "device_id": session.device_id,
            "is_revoked": session.is_revoked,
            "is_active": (not session.is_revoked and session.expires_at > now),
            "created_at": session.created_at,
            "expires_at": session.expires_at,
        }
