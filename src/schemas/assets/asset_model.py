from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AssetModelCreateSchema(BaseModel):
    name: str
    manufacturer_id: UUID
    category_id: UUID

    lifetime_years: int | None = Field(default=None, ge=0)
    warranty_months: int | None = Field(default=None, ge=0)


class AssetModelOutSchema(BaseModel):
    id: UUID
    name: str
    code: str

    manufacturer_id: UUID
    category_id: UUID

    lifetime_years: int | None
    warranty_months: int | None

    model_config = ConfigDict(from_attributes=True)
