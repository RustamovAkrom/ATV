from uuid import UUID

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.enums import UserStatus
from db.models.users import Role, User
from schemas.pagination_schema import PaginationParamsSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self, include_inactive: bool = False):
        query = select(User).options(
            selectinload(User.role).selectinload(Role.permissions)
        )

        if not include_inactive:
            query = query.where(User.status == UserStatus.ACTIVE.value)

        return query

    async def get_by_id(self, user_id: UUID, include_inactive=False) -> User | None:
        result = await self.session.execute(
            self._base_query(include_inactive).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str, include_inactive=False) -> User | None:
        result = await self.session.execute(
            self._base_query(include_inactive).where(User.login == login)
        )
        return result.scalar_one_or_none()

    async def get_by_identity(self, identity: str) -> User | None:
        result = await self.session.execute(
            self._base_query().where(
                or_(User.login == identity, User.email == identity)
            )
        )
        return result.scalar_one_or_none()

    async def list(self, pagination: PaginationParamsSchema) -> list[User]:
        result = await self.session.execute(
            self._base_query().limit(pagination.limit).offset(pagination.offset())
        )
        return result.scalars().all()

    async def search(self, query: str, pagination: PaginationParamsSchema):
        result = await self.session.execute(
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
        return result.scalars().all()

    async def exists_by_email(self, email: str) -> bool:
        result = await self.session.execute(
            select(User.id).where(User.email == email).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def exists_by_login(self, login: str) -> bool:
        result = await self.session.execute(
            select(User.id).where(User.login == login).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user_id: UUID, data: dict) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**data)
        )

    async def set_password(self, user_id: UUID, password_hash: str):
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(password_hash=password_hash)
        )

    async def change_status(self, user_id: UUID, status: str):
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(status=status)
        )

    async def update_role(self, user_id: UUID, role_id: UUID) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(role_id=role_id)
        )

    async def get_all_with_inactive(self, limit: int, offset: int):
        result = await self.session.execute(
            self._base_query(include_inactive=True)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def set_permissions(self, user: User, permissions: list) -> None:
        user.permissions = permissions
        await self.session.flush()
