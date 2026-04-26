from uuid import UUID

from pydantic import BaseModel, ConfigDict, HttpUrl


class ManufacturerCreateSchema(BaseModel):
    name: str
    country: str | None = None
    website: HttpUrl | None = None


class ManufacturerOutSchema(BaseModel):
    id: UUID
    name: str
    code: str
    country: str | None
    website: str | None

    model_config = ConfigDict(from_attributes=True)
