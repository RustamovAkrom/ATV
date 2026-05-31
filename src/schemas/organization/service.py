from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from schemas.base import BaseSchema, TimestampSchema


class ServiceBaseSchema(BaseSchema):
    name: str = Field(min_length=2, max_length=255, description="Service name")
    description: str | None = Field(
        None, max_length=500, description="Service description"
    )
    region_ids: list[UUID] | None = Field(None, description="IDs of attached regions")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Очистка и валидация имени"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Service name cannot be empty")
        return cleaned


class ServiceCreateSchema(ServiceBaseSchema):
    """Схема для создания сервиса"""

    pass


class ServiceUpdateSchema(BaseSchema):
    """Схема для обновления сервиса"""

    name: str | None = Field(
        None, min_length=2, max_length=255, description="Service name"
    )
    description: str | None = Field(
        None, max_length=500, description="Service description"
    )
    region_ids: list[UUID] | None = Field(None, description="IDs of attached regions")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Очистка и валидация имени"""
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Service name cannot be empty")
            return cleaned
        return v


class ServiceOutSchema(TimestampSchema):
    """Схема для вывода сервиса"""

    id: UUID
    name: str
    slug: str | None  # <-- исправлено: может быть None при создании?
    description: str | None
    region_ids: list[UUID] | None = Field(None, description="IDs of attached regions")


class ServiceWithRegionsOutSchema(ServiceOutSchema):
    """Schema for service output with regions"""

    regions: list[dict[str, Any]] | None = Field(None, description="Attached regions")
