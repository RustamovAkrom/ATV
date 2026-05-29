# schemas/asset_class.py

from uuid import UUID

from pydantic import Field

from schemas.base import BaseSchema


class AssetClassCreateSchema(BaseSchema):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class AssetClassOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str
    description: str | None
