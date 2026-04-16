from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.auth.password_reset import PasswordReset


class PasswordResetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: PasswordReset):
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get_valid(self, token_hash: str) -> PasswordReset | None:
        result = await self.session.execute(
            select(PasswordReset)
            .where(
                PasswordReset.token_hash == token_hash,
                PasswordReset.is_used == False,
                PasswordReset.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalar_one_or_none()

    async def mark_used(self, reset_id: UUID):
        await self.session.execute(
            update(PasswordReset)
            .where(PasswordReset.id == reset_id)
            .values(is_used=True)
        )
