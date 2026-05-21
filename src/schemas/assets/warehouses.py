from datetime import datetime
from uuid import UUID
from pydantic import Field, field_validator

from schemas.base import BaseSchema, TimestampSchema


class WarehouseBaseSchema(BaseSchema):
    """Базовые поля склада"""
    name: str = Field(min_length=2, max_length=150, description="Название склада")
    slug: str | None = Field(None, max_length=50, description="Уникальный код склада")
    region_id: UUID = Field(..., description="ID региона")
    service_id: UUID | None = Field(None, description="ID сервиса")
    manager_user_id: UUID | None = Field(None, description="ID ответственного пользователя")
    is_active: bool = Field(True, description="Активен ли склад")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Warehouse name cannot be empty")
        return cleaned

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip().upper()
            if not cleaned:
                return None
            return cleaned
        return v


class WarehouseCreateSchema(WarehouseBaseSchema):
    """Схема для создания склада"""
    pass


class WarehouseUpdateSchema(BaseSchema):
    """Схема для обновления склада"""
    name: str | None = Field(None, min_length=2, max_length=150)
    slug: str | None = Field(None, max_length=50)
    region_id: UUID | None = None
    service_id: UUID | None = None
    manager_user_id: UUID | None = None
    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Warehouse name cannot be empty")
            return cleaned
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip().upper()
            if not cleaned:
                return None
            return cleaned
        return v


class WarehouseOutSchema(TimestampSchema):
    """Схема для ответа"""
    id: UUID
    name: str
    slug: str | None
    region_id: UUID
    service_id: UUID | None
    manager_user_id: UUID | None
    is_active: bool
    assets_count: int | None = Field(None, description="Количество активов на складе")


class WarehouseWithDetailsOutSchema(WarehouseOutSchema):
    """Склад с деталями (регион, сервис, менеджер)"""
    region_name: str | None = None
    service_name: str | None = None
    manager_name: str | None = None

class WarehouseMoveRequest(BaseSchema):
    """Запрос на перемещение актива на склад"""
    warehouse_id: UUID = Field(..., description="ID целевого склада")

