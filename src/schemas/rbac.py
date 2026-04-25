from typing import List, Optional
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
    permissions: List[PermissionOutSchema] = []
    model_config = ConfigDict(from_attributes=True)


class RoleCreateSchema(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class RoleUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str] = None


class RolePermissionsUpdateSchema(BaseModel):
    permission_ids: List[UUID]
