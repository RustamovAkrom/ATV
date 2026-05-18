from decimal import Decimal
from uuid import UUID

from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema


class PartCreateSchema(BaseSchema):
    name: str = Field(min_length=2, max_length=150)
    code: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)
    unit_price: Decimal | None = Field(None, ge=0, decimal_places=2)


class PartUpdateSchema(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=150)
    code: str | None = Field(None, max_length=50)
    description: str | None = Field(None, max_length=500)
    unit_price: Decimal | None = Field(None, ge=0, decimal_places=2)


class PartOutSchema(TimestampSchema):
    id: UUID
    name: str
    code: str | None
    description: str | None
    unit_price: Decimal | None
