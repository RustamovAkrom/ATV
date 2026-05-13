from uuid import UUID

from schemas.base import BaseSchema


class AssetCategoryCreateSchema(BaseSchema):
    name: str
    # code: str


class AssetCategoryUpdateSchema(BaseSchema):
    name: str | None = None
    code: str | None = None


class AssetCategoryOutSchema(BaseSchema):
    id: UUID
    name: str
    code: str
