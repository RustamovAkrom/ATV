from typing import Any
from uuid import UUID

from pydantic import Field, field_validator

from schemas.base import BaseRequestSchema, BaseSchema, TimestampSchema


class RegionBaseSchema(BaseRequestSchema):
    """Базовые поля региона"""

    name: str = Field(min_length=2, max_length=255, description="Название региона")
    parent_id: UUID | None = Field(None, description="ID родительского региона")
    latitude: float | None = Field(None, ge=-90, le=90, description="Широта")
    longitude: float | None = Field(None, ge=-180, le=180, description="Долгота")
    geojson: dict | None = Field(None, description="GeoJSON данные")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Очистка и валидация имени"""
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Region name cannot be empty")
        return cleaned

class RegionCreateSchema(RegionBaseSchema):
    """Схема для создания региона"""

    pass

class RegionUpdateSchema(BaseRequestSchema):
    """Схема для обновления региона (все поля опциональны)"""

    name: str | None = Field(
        None, min_length=2, max_length=255, description="Название региона"
    )
    parent_id: UUID | None = Field(None, description="ID родительского региона")
    latitude: float | None = Field(None, ge=-90, le=90, description="Широта")
    longitude: float | None = Field(None, ge=-180, le=180, description="Долгота")
    geojson: dict | None = Field(None, description="GeoJSON данные")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Очистка и валидация имени"""
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Region name cannot be empty")
            return cleaned
        return v

class RegionOutSchema(TimestampSchema):
    """Схема для ответа (вывод региона)"""

    id: UUID
    name: str
    latitude: float | None
    longitude: float | None
    geojson: dict | None
    parent_id: UUID | None
    level: int | None = Field(None, description="Уровень в иерархии")

    @field_validator("id", mode="before")
    @classmethod
    def validate_uuid(cls, v: Any) -> Any:
        """Валидация UUID"""
        return v

class RegionTreeOutSchema(RegionOutSchema):
    """Схема для древовидного вывода региона"""

    children: list["RegionTreeOutSchema"] = Field(
        default_factory=list, description="Дочерние регионы"
    )

class RegionWithServicesOutSchema(RegionOutSchema):
    """Region with attached services"""

    service_ids: list[UUID] | None = Field(None, description="ID сервисов в регионе")
    service_names: list[str] | None = Field(None, description="Названия сервисов")

class RegionStatsOutSchema(BaseSchema):
    """Статистика по региону"""

    region_id: UUID
    region_name: str
    total_assets: int = Field(0, description="Total assets")
    active_assets: int = Field(0, description="Active assets")
    users_count: int = Field(0, description="Number of users")
    services_count: int = Field(0, description="Количество сервисов")

# Регистрация рекурсивной модели
RegionTreeOutSchema.model_rebuild()
