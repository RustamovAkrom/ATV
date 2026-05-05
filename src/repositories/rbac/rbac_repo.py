from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.users.permission import Permission, Role
from repositories.base import BaseRepository


class RBACRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    # ROLES
    async def get_roles(self):
        return await self.scalars(
            select(Role).options(selectinload(Role.permissions))
        )

    async def get_role(self, role_id: UUID):
        return await self.scalar(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )

    async def exists_by_code(self, code: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(Role.id).where(Role.code == code)
        if exclude_id:
            stmt = stmt.where(Role.id != exclude_id)

        return await self.scalar(stmt) is not None

    async def exists_by_name(self, name: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(Role.id).where(Role.name == name)
        if exclude_id:
            stmt = stmt.where(Role.id != exclude_id)

        return await self.scalar(stmt) is not None

    async def create_role(self, role: Role):
        self.add(role)
        await self.flush()
        await self.session.refresh(role, ["permissions"])
        return role

    async def update_role(self, role_id: UUID, data: dict):
        role = await self.get_role(role_id)
        if not role:
            return None

        for k, v in data.items():
            setattr(role, k, v)

        await self.flush()
        await self.session.refresh(role, ["permissions"])
        return role

    async def delete_role(self, role_id: UUID):
        await self.execute(delete(Role).where(Role.id == role_id))

    # PERMISSIONS
    async def get_permissions(self):
        return await self.scalars(select(Permission))

    async def get_permissions_by_ids(self, ids: list[UUID]):
        if not ids:
            return []

        return await self.scalars(
            select(Permission).where(Permission.id.in_(ids))
        )

    # ROLE-PERMISSIONS
    async def set_role_permissions(self, role: Role, permissions: list[Permission]):
        role.permissions = permissions
        await self.flush()
