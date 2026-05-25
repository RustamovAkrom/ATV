from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_default=True,
        extra="forbid",  # forbidden extra fields
    )


class TimestampSchema(BaseSchema):
    created_at: datetime
    updated_at: datetime


class UUIDRefSchema(BaseSchema):
    id: UUID


class NamedRefSchema(UUIDRefSchema):
    name: str


class UserRefSchema(NamedRefSchema):
    login: str | None = None
