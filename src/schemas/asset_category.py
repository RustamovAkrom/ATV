from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssetCategoryCreateSchema(BaseModel):
    name: str
    # code: str


class AssetCategoryUpdateSchema(BaseModel):
    name: str | None = None
    code: str | None = None


class AssetCategoryOutSchema(BaseModel):
    id: UUID
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)
