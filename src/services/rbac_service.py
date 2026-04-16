from uuid import UUID

from core.exceptions.errors import InvalidToken
from db.models.users.permission import Role
from repositories.rbac_repo import RBACRepository
from schemas.rbac import RoleCreate


class RBACService:
    def __init__(self, rbac_repo: RBACRepository):
        self.rbac_repo = rbac_repo

    # ROLES
    async def list_roles(self):
        return await self.rbac_repo.get_roles()

    async def get_role(self, role_id: UUID):
        role = await self.rbac_repo.get_role(role_id)
        if not role:
            raise InvalidToken()
        return role

    async def create_role(self, data: RoleCreate):
        role = Role(
            name=data.name,
            code=data.code,
            description=data.description,
        )
        return await self.rbac_repo.create_role(role)

    async def update_role(self, role_id: UUID, data: dict):
        role = await self.rbac_repo.get_role(role_id)
        if not role:
            raise InvalidToken()
        return await self.rbac_repo.update_role(role_id, data)

    async def delete_role(self, role_id: UUID):
        role = await self.rbac_repo.get_role(role_id)
        if not role:
            raise InvalidToken()
        await self.rbac_repo.delete_role(role_id)

    # PERMISSIONS
    async def list_permissions(self):
        return await self.rbac_repo.get_permissions()

    # ROLE-PERMISSIONS
    async def set_role_permissions(self, role_id: UUID, permission_ids: list[UUID]):
        role = await self.rbac_repo.get_role(role_id)
        if not role:
            raise InvalidToken()

        permissions = await self.rbac_repo.get_permissions_by_ids(permission_ids)

        await self.rbac_repo.set_role_permissions(role, permissions)

        return role
