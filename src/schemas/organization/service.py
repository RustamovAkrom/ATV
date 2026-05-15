from uuid import UUID
from typing import Any
from pydantic import Field, field_validator

from schemas.base import BaseSchema, TimestampSchema


class ServiceBaseSchema(BaseSchema):
    name: str = Field(min_length=2, max_length=255, description="Service name")
    description: str | None = Field(None, max_length=500, description="Service description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Очистка и валидация имени"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Region name cannot be empty")
        return cleaned


class ServiceCreateSchema(ServiceBaseSchema):
    pass


class ServiceUpdateSchema(BaseSchema):
    name: str | None = Field(None, min_length=2, max_length=255, description="Service name")
    description: str | None = Field(None, max_length=500, description="Service description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str | None:
        """Очистка и валидация имени"""
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Region name cannot be empty")
            return cleaned
        return v


class ServiceOutSchema(TimestampSchema):
    id: UUID
    name: str
    description: str | None
    region_ids: list[UUID] | None = Field(None, description="IDs attached regions")


class ServiceWithRegionsOutSchema(ServiceOutSchema):
    regions: list[dict[str, Any]] | None = Field(None, description="Attached regions")
