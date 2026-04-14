from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import List, Optional


class PermissionOut(BaseModel):
    id: UUID
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)


class RoleOut(BaseModel):
    id: UUID
    name: str
    code: str
    permissions: List[PermissionOut]

    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    name: str
    code: str
    description: Optional[str]


class RoleUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class RolePermissionsUpdate(BaseModel):
    permission_ids: List[UUID]
