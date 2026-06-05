from uuid import UUID

from pydantic import Field

from schemas.base import BaseRequestSchema, BaseSchema


class AssetModelCreateSchema(BaseRequestSchema):
    name: str
    manufacturer_id: UUID
    category_id: UUID

    lifetime_years: int | None = Field(default=None, ge=0)
    warranty_months: int | None = Field(default=None, ge=0)


class AssetModelOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str

    manufacturer_id: UUID
    category_id: UUID

    lifetime_years: int | None
    warranty_months: int | None
