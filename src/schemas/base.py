from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseRequestSchema(BaseModel):
    """Base class for incoming API payloads."""

    model_config = ConfigDict(
        from_attributes=False,
        populate_by_name=True,
        use_enum_values=True,
        validate_default=True,
        extra="forbid",
    )


class BaseResponseSchema(BaseModel):
    """Base class for outgoing API payloads and ORM serialization."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_default=True,
        extra="ignore",
    )


class BaseSchema(BaseResponseSchema):
    """Backward-compatible response schema base."""


class TimestampSchema(BaseResponseSchema):
    created_at: datetime
    updated_at: datetime


class UUIDRefSchema(BaseResponseSchema):
    id: UUID


class NamedRefSchema(UUIDRefSchema):
    name: str


class UserRefSchema(NamedRefSchema):
    login: str | None = None
