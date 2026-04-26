from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from db.models.auth.password_reset import PasswordReset
from utils.helpers import utc_now


class PasswordResetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: PasswordReset):
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def use_token(self, token_hash: str) -> PasswordReset | None:
        stmt = (
            update(PasswordReset)
            .where(
                PasswordReset.token_hash == token_hash,
                PasswordReset.is_used.is_(False),
                PasswordReset.expires_at > func.now(),
            )
            .values(is_used=True)
            .returning(PasswordReset)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def clean_old(self, user_id: UUID):
        await self.session.execute(
            delete(PasswordReset).where(PasswordReset.user_id == user_id)
        )

    async def count_active_resets(self, user_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(
                PasswordReset.user_id == user_id,
                PasswordReset.is_used.is_(False),
                PasswordReset.expires_at > utc_now(),
            )
        )
        return result.scalar_one()

    # async def get_valid(self, token_hash: str) -> PasswordReset | None:
    #     result = await self.session.execute(
    #         select(PasswordReset)
    #         .where(
    #             PasswordReset.token_hash == token_hash,
    #             PasswordReset.is_used == False,
    #             PasswordReset.expires_at > datetime.now(timezone.utc),
    #         )
    #     )
    #     return result.scalar_one_or_none()

    # async def mark_used(self, reset_id: UUID):
    #     await self.session.execute(
    #         update(PasswordReset)
    #         .where(PasswordReset.id == reset_id)
    #         .values(is_used=True)
    #     )
