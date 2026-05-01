from uuid import UUID

from sqlalchemy import or_, select, update, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.enums import UserStatus
from db.models.users import Role, User
from schemas.pagination import PaginationParamsSchema
from repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self, include_inactive: bool = False):
        query = select(User).options(
            selectinload(User.role).selectinload(Role.permissions),
            selectinload(User.direct_permissions),  # ✅ FIX
        )

        if not include_inactive:
            query = query.where(User.status == UserStatus.ACTIVE.value)

        return query

    async def get_by_id(self, user_id: UUID, include_inactive=False) -> User | None:
        return await self.scalar(
            self._base_query(include_inactive).where(User.id == user_id)
        )

    async def get_by_login(self, login: str, include_inactive=False) -> User | None:
        return await self.scalar(
            self._base_query(include_inactive).where(User.login == login)
        )

    async def get_by_identity(self, identity: str) -> User | None:
        return await self.scalar(
            self._base_query().where(
                or_(User.login == identity, User.email == identity)
            )
        )

    async def list(self, pagination: PaginationParamsSchema) -> list[User]:
        return await self.scalars(
            self._base_query()
            .order_by(User.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset())
        )

    async def search(self, query: str, pagination: PaginationParamsSchema):
        query = query.strip()[:100]
        return await self.scalars(
            self._base_query(include_inactive=True)
            .where(
                or_(
                    User.login.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                )
            )
            .limit(pagination.limit)
            .offset(pagination.offset())
        )

    async def exists_by_email(self, email: str) -> bool:
        return await self.scalar(select(exists().where(User.email == email))) is not None

    async def exists_by_login(self, login: str) -> bool:
        return await self.session.scalar(select(exists()).where(User.login == login).limit(1)) is not None

    async def create(self, user: User) -> User:
        self.add(user)
        await self.flush()
        return user

    async def update(self, user_id: UUID, data: dict) -> None:
        await self.execute(
            update(User).where(User.id == user_id).values(**data)
        )
        await self.flush()

    async def set_password(self, user_id: UUID, password_hash: str):
        await self.execute(
            update(User).where(User.id == user_id).values(password_hash=password_hash)
        )
        await self.flush()

    async def change_status(self, user_id: UUID, status: str):
        await self.execute(
            update(User).where(User.id == user_id).values(status=status)
        )

    async def update_role(self, user_id: UUID, role_id: UUID) -> None:
        await self.execute(
            update(User).where(User.id == user_id).values(role_id=role_id)
        )

    async def get_all_with_inactive(self, limit: int, offset: int):
        return await self.scalars(
            self._base_query(include_inactive=True).limit(limit).offset(offset)
        )

    async def set_permissions(self, user: User, permissions: list) -> None:
        user.direct_permissions = permissions
        await self.flush()
