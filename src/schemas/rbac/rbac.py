from uuid import UUID

from pydantic import Field

from schemas.base import BaseSchema


class PermissionOutSchema(BaseSchema):
    id: UUID
    name: str = Field(max_length=255)
    slug: str = Field(max_length=50, pattern=r"^[a-z][a-z0-9._]*$")


class RoleOutSchema(BaseSchema):
    id: UUID
    name: str = Field(max_length=100)
    slug: str = Field(max_length=50)
    description: str | None = Field(None, max_length=500)
    permissions: list[PermissionOutSchema] = Field(default_factory=list)


class RoleCreateSchema(BaseSchema):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=50, pattern=r"^[a-z][a-z0-9_]*$")
    description: str | None = Field(None, max_length=500)


class RoleUpdateSchema(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)


class RolePermissionsUpdateSchema(BaseSchema):
    permission_ids: list[UUID] = Field(
        min_length=1, description="List of permission IDs to assign"
    )
