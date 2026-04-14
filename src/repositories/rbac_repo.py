from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.users.permission import Role, Permission, role_permissions


class RBACRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ROLES
    async def get_roles(self):
        result = await self.session.execute(
            select(Role).options(selectinload(Role.permissions))
        )
        return result.scalars().all()

    async def get_role(self, role_id: UUID):
        result = await self.session.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        return result.scalar_one_or_none()

    async def create_role(self, role: Role):
        self.session.add(role)
        await self.session.flush()
        return role

    async def update_role(self, role_id: UUID, data: dict):
        role = await self.get_role(role_id)
        for k, v in data.items():
            setattr(role, k, v)
        return role

    async def delete_role(self, role_id: UUID):
        await self.session.execute(
            delete(Role).where(Role.id == role_id)
        )

    # PERMISSIONS
    async def get_permissions(self):
        result = await self.session.execute(select(Permission))
        return result.scalars().all()

    async def get_permissions_by_ids(self, ids: list[UUID]):
        result = await self.session.execute(
            select(Permission).where(Permission.id.in_(ids))
        )
        return result.scalars().all()

    # ROLE-PERMISSIONS
    async def set_role_permissions(self, role: Role, permissions: list[Permission]):
        role.permissions = permissions
        await self.session.flush()
