from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.users import User, Role
from db.dependencies import get_db_session


class UserRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_by_login(self, login: str) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.login == login)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()


def get_user_repo(
    db: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    return UserRepository(db)
