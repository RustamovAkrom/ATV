# schemas/asset_class.py

from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AssetClassCreateSchema(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class AssetClassOutSchema(BaseModel):
    id: UUID
    name: str
    code: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
