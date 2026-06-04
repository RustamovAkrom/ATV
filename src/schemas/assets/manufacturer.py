from uuid import UUID

from pydantic import HttpUrl

from schemas.base import BaseRequestSchema, BaseSchema


class ManufacturerCreateSchema(BaseRequestSchema):
    name: str
    country: str | None = None
    website: HttpUrl | None = None


class ManufacturerOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str
    country: str | None
    website: str | None
