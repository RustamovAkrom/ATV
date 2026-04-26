from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionOutSchema(BaseModel):
    id: UUID
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class RoleOutSchema(BaseModel):
    id: UUID
    name: str
    code: str
    permissions: list[PermissionOutSchema] = []
    model_config = ConfigDict(from_attributes=True)


class RoleCreateSchema(BaseModel):
    name: str
    code: str
    description: str | None = None


class RoleUpdateSchema(BaseModel):
    name: str | None
    description: str | None = None


class RolePermissionsUpdateSchema(BaseModel):
    permission_ids: list[UUID]
