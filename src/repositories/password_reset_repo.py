from uuid import UUID
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from db.models.auth.password_reset import PasswordReset
from db.dependencies import get_db_session


class PasswordResetRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
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
                PasswordReset.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def mark_used(self, reset_id: UUID):
        await self.session.execute(
            update(PasswordReset)
            .where(PasswordReset.id == reset_id)
            .values(is_used=True)
        )


def get_reset_repo(
    db: AsyncSession = Depends(get_db_session),
) -> PasswordResetRepository:
    return PasswordResetRepository(db)
