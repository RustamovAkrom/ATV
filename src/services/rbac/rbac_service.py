from uuid import UUID

from sqlalchemy.exc import IntegrityError

from core.exceptions.errors import BadRequest, NotFound, ValidationError
from db.models.users.permission import Role
from repositories.rbac.rbac_repo import RBACRepository
from schemas.rbac.rbac import RoleCreateSchema, RoleUpdateSchema


class RBACService:
    def __init__(self, rbac_repo: RBACRepository):
        self.rbac_repo = rbac_repo

    # ROLES
    async def list_roles(self):
        return await self.rbac_repo.get_roles()

    async def get_role(self, role_id: UUID):
        try:
            role = await self.rbac_repo.get_role(role_id)
            if not role:
                raise NotFound("Role not found")
            return role
        except IntegrityError as e:
            raise BadRequest("Role with this code already exists") from e

    async def create_role(self, data: RoleCreateSchema):
        # normalize
        code = data.code.lower().strip()

        if await self.rbac_repo.exists_by_code(code):
            raise ValidationError("Role code already exists")

        if await self.rbac_repo.exists_by_name(data.name):
            raise ValidationError("Role name already exists")

        try:
            role = Role(
                name=data.name.strip(),
                code=code,
                description=(data.description or "").strip() or None,
            )
            return await self.rbac_repo.create_role(role)
        except IntegrityError as e:
            raise BadRequest("Role with this code already exists") from e

    async def update_role(self, role_id: UUID, data: RoleUpdateSchema):
        role = await self.rbac_repo.get_role(role_id)
        if not role:
            raise NotFound("Role not found")

        payload = data.model_dump(exclude_unset=True)

        if "code" in payload and payload["code"]:
            payload["code"] = payload["code"].lower().strip()
            if await self.rbac_repo.exists_by_code(payload["code"], exclude_id=role_id):
                raise ValidationError("Role code already exists")

        if "name" in payload and payload["name"]:
            payload["name"] = payload["name"].strip()
            if await self.rbac_repo.exists_by_name(payload["name"], exclude_id=role_id):
                raise ValidationError("Role name already exists")

        return await self.rbac_repo.update_role(role_id, payload)

    async def delete_role(self, role_id: UUID):
        role = await self.rbac_repo.get_role(role_id)
        if not role:
            raise BadRequest("Role not found")

        # safety:
        if role.users:
            raise BadRequest("Cannot delete role with assigned users")

        await self.rbac_repo.delete_role(role_id)

    # PERMISSIONS
    async def list_permissions(self):
        return await self.rbac_repo.get_permissions()

    # ROLE-PERMISSIONS
    async def set_role_permissions(self, role_id: UUID, permission_ids: list[UUID]):
        role = await self.rbac_repo.get_role(role_id)
        if not role:
            raise NotFound("Role not found")

        # remove duplicates early
        permission_ids = list(set(permission_ids))

        permissions = await self.rbac_repo.get_permissions_by_ids(permission_ids)

        if len(permissions) != len(permission_ids):
            raise ValidationError("Some permissions not found")

        await self.rbac_repo.set_role_permissions(role, permissions)

        return role
