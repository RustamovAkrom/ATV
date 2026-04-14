from uuid import UUID

from core.exceptions.errors import InvalidToken, AuthenticationError
from repositories.user_repo import UserRepository
from db.models.users import User
from schemas.users import UserCreate, UserUpdate, AdminUserUpdate
from core.security.passwords import hash_password, verify_password
from db.models.enums import UserStatus


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_all(self, limit: int, offset: int):
        return await self.user_repo.get_iall(limit, offset)

    async def get(self, user_id: UUID):
        user = await self.user_repo.get_by_id(user_id, include_inactive=True)
        if not user:
            raise InvalidToken()
        return user

    async def create(self, data: UserCreate):
        if await self.user_repo.exists_by_email(data.email):
            raise AuthenticationError("Email already exists")

        if await self.user_repo.exists_by_login(data.login):
            raise AuthenticationError("Login already exists")

        user = User(
            login=data.login,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role_id=data.role_id,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return await self.user_repo.create(user)

    async def update(self, user_id: UUID, data: UserUpdate):
        await self.user_repo.update(
            user_id,
            data.model_dump(exclude_unset=True),
        )
        return await self.get(user_id)

    async def admin_update(self, user_id: UUID, data: AdminUserUpdate):
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
        user = await self.user_repo.get_by_id(user_id, include_inactive=True)

        if not verify_password(old_password, user.password_hash):
            raise AuthenticationError("Invalid password")

        await self.user_repo.set_password(
            user_id,
            hash_password(new_password)
        )

    async def activate(self, user_id: UUID):
        await self.user_repo.change_status(user_id, UserStatus.ACTIVE.value)

    async def archive(self, user_id: UUID):
        await self.user_repo.change_status(user_id, UserStatus.ARCHIVED.value)

    async def block(self, user_id: UUID):
        await self.user_repo.change_status(user_id, UserStatus.BLOCKED.value)
