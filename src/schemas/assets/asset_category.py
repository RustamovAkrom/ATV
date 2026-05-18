from uuid import UUID

from schemas.base import BaseSchema


class AssetCategoryCreateSchema(BaseSchema):
    name: str
    slug: str


class AssetCategoryUpdateSchema(BaseSchema):
    name: str | None = None
    slug: str | None = None


class AssetCategoryOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str
