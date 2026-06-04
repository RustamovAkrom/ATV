from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from schemas.base import BaseRequestSchema, BaseSchema, TimestampSchema


class DepartmentBaseSchema(BaseRequestSchema):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    region_id: UUID
    parent_id: UUID | None = None
    service_ids: list[UUID] = Field(default_factory=list)
    address: str | None = Field(None, max_length=500)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    contact_phone: str | None = Field(None, max_length=50)
    contact_email: str | None = Field(None, max_length=255)
    is_active: bool = True
    meta: dict[str, Any] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Department name cannot be empty")
        return cleaned

    @field_validator("service_ids")
    @classmethod
    def dedupe_service_ids(cls, value: list[UUID]) -> list[UUID]:
        return list(dict.fromkeys(value))


class DepartmentCreateSchema(DepartmentBaseSchema):
    pass


class DepartmentUpdateSchema(BaseRequestSchema):
    name: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=1000)
    region_id: UUID | None = None
    parent_id: UUID | None = None
    service_ids: list[UUID] | None = None
    address: str | None = Field(None, max_length=500)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    contact_phone: str | None = Field(None, max_length=50)
    contact_email: str | None = Field(None, max_length=255)
    is_active: bool | None = None
    meta: dict[str, Any] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Department name cannot be empty")
        return cleaned

    @field_validator("service_ids")
    @classmethod
    def dedupe_service_ids(cls, value: list[UUID] | None) -> list[UUID] | None:
        if value is None:
            return value
        return list(dict.fromkeys(value))


class DepartmentRegionRefSchema(BaseSchema):
    id: UUID
    name: str
    latitude: float | None = None
    longitude: float | None = None


class DepartmentServiceRefSchema(BaseSchema):
    id: UUID
    name: str
    slug: str | None = None


class DepartmentOutSchema(TimestampSchema):
    id: UUID
    name: str
    slug: str | None
    description: str | None
    region_id: UUID
    parent_id: UUID | None
    service_ids: list[UUID] = Field(default_factory=list)
    address: str | None
    latitude: float | None
    longitude: float | None
    contact_phone: str | None
    contact_email: str | None
    is_active: bool
    meta: dict[str, Any] = Field(default_factory=dict)


class DepartmentDetailSchema(DepartmentOutSchema):
    region: DepartmentRegionRefSchema
    services: list[DepartmentServiceRefSchema] = Field(default_factory=list)
