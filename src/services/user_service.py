from uuid import UUID

from core.exceptions.errors import AuthenticationError, BadRequest, NotFound
from core.security.passwords import hash_password, verify_password
from db.models.enums import UserStatus
from db.models.users import User
from repositories.rbac_repo import RBACRepository
from repositories.user_repo import UserRepository
from schemas.pagination_schema import PaginationParamsSchema
from schemas.users_schema import (AdminUserUpdateSchema, UserCreateSchema,
                                  UserUpdateSchema)
from utils.helpers import utc_now


class UserService:
    def __init__(self, user_repo: UserRepository, rbac_repo: RBACRepository):
        self.user_repo = user_repo
        self.rbac_repo = rbac_repo

    async def get_all(self, pagination: PaginationParamsSchema):
        return await self.user_repo.list(pagination)

    async def search(self, query: str, pagination: PaginationParamsSchema):
        return await self.user_repo.search(query, pagination)

    async def get(self, user_id: UUID):
        user = await self.user_repo.get_by_id(user_id, include_inactive=True)
        if not user:
            raise BadRequest("User not found")
        return user

    async def create(self, data: UserCreateSchema):
        if await self.user_repo.exists_by_email(data.email):
            raise BadRequest("Email already exists")

        if await self.user_repo.exists_by_login(data.login):
            raise BadRequest("Login already exists")

        role = await self.rbac_repo.get_role(data.role_id)
        if not role:
            raise BadRequest("Invalid role")

        user = User(
            login=data.login,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role_id=data.role_id,
            first_name=data.first_name,
            last_name=data.last_name,
            status=UserStatus.ACTIVE.value,
        )
        user = await self.user_repo.create(user)
        return user

    async def update(self, user_id: UUID, data: UserUpdateSchema):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFound("User not found")

        await self.user_repo.update(
            user_id,
            data.model_dump(exclude_unset=True),
        )

        return await self.get(user_id)

    async def admin_update(self, user_id: UUID, data: AdminUserUpdateSchema):
        await self.get(user_id)

        if data.role_id:
            role = await self.rbac_repo.get_role(data.role_id)
            if not role:
                raise BadRequest("Invalid role")

        await self.user_repo.update(
            user_id,
            data.model_dump(exclude_unset=True),
        )

        return await self.get(user_id)

    async def change_password(
        self,
        user_id: UUID,
        old_password: str,
        new_password: str,
    ):
        user = await self.get(user_id)

        if not verify_password(old_password, user.password_hash):
            raise AuthenticationError("Invalid password")

        await self.user_repo.set_password(
            user_id,
            hash_password(new_password)
        )
        await self.user_repo.update(
            user_id,
            {"last_password_change": utc_now()},
        )

    async def activate(self, user_id: UUID):
        await self.user_repo.change_status(user_id, UserStatus.ACTIVE.value)

    async def archive(self, user_id: UUID):
        await self.user_repo.change_status(user_id, UserStatus.ARCHIVED.value)

    async def block(self, user_id: UUID):
        await self.user_repo.change_status(user_id, UserStatus.BLOCKED.value)
