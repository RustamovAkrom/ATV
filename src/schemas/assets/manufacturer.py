from uuid import UUID

from pydantic import ConfigDict, HttpUrl
from schemas.base import BaseSchema


class ManufacturerCreateSchema(BaseSchema):
    name: str
    country: str | None = None
    website: HttpUrl | None = None


class ManufacturerOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str
    country: str | None
    website: str | None
