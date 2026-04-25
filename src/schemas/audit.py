# src/schemas/audit.py

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =========================
# BASE (общая модель)
# =========================
class AuditBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    path: str
    status_code: int
    user_id: Optional[uuid.UUID]
    request_id: str
    latency_ms: int
    ip: Optional[str]
    user_agent: Optional[str]
    is_suspicious: bool
    query: Optional[str]

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("path")
    @classmethod
    def normalize_path(cls, value: str) -> str:
        return value.strip()

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class AuditCreateSchema(AuditBaseSchema):
    pass


class AuditSchema(AuditBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class AuditStreamSchema(AuditBaseSchema):
    model_config = ConfigDict(extra="forbid")

    level: str
    timestamp: float


class AuditFiltersSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: uuid.UUID | None = None
    request_id: str | None = Field(default=None, max_length=128)
    method: str | None = Field(default=None, max_length=16)
    status_code: int | None = Field(default=None, ge=100, le=599)
    status_min: int | None = Field(default=None, ge=100, le=599)
    status_max: int | None = Field(default=None, ge=100, le=599)
    from_date: datetime | None = None
    to_date: datetime | None = None
    search: str | None = Field(default=None, max_length=256)
    is_suspicious: bool | None = None

    @field_validator("method")
    @classmethod
    def normalize_method(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip().upper()
        return value or None

    @field_validator("search")
    @classmethod
    def normalize_search(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value


class AuditStatsSchema(BaseModel):
    total: int
    errors: int
    server_errors: int

    suspicious: int
