from datetime import datetime
from uuid import UUID

from pydantic import Field

from schemas.base import BaseRequestSchema, BaseSchema


class PermissionOutSchema(BaseSchema):
    id: UUID
    name: str = Field(max_length=255)
    slug: str = Field(max_length=50)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RoleOutSchema(BaseSchema):
    id: UUID
    name: str = Field(max_length=100)
    slug: str = Field(max_length=50)
    description: str | None = Field(None, max_length=500)
    permissions: list[PermissionOutSchema] = Field(default_factory=list)


class RoleCreateSchema(BaseRequestSchema):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=50, pattern=r"^[a-z][a-z0-9_]*$")
    description: str | None = Field(None, max_length=500)


class RoleUpdateSchema(BaseRequestSchema):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)


class RolePermissionsUpdateSchema(BaseRequestSchema):
    permission_ids: list[UUID] = Field(
        min_length=1, description="List of permission IDs to assign"
    )
