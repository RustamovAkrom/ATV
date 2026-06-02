from uuid import UUID

from schemas.base import BaseRequestSchema, BaseSchema


class AssetCategoryCreateSchema(BaseRequestSchema):
    name: str

class AssetCategoryUpdateSchema(BaseRequestSchema):
    name: str | None = None

class AssetCategoryOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str
