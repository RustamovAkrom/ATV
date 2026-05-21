from uuid import UUID
from datetime import date, datetime
from pydantic import Field, field_validator

from schemas.base import BaseSchema, TimestampSchema


class AssetMaintenanceBaseSchema(BaseSchema):
    """Базовые поля техобслуживания"""
    maintenance_type: str = Field(min_length=2, max_length=100)
    performed_at: date = Field(...)
    issues_found: str | None = Field(None, max_length=1000)
    performed_by_id: UUID = Field(...)
    notes: str | None = Field(None, max_length=1000)


class AssetMaintenanceCreateSchema(AssetMaintenanceBaseSchema):
    """Создание записи техобслуживания"""
    pass


class AssetMaintenanceUpdateSchema(BaseSchema):
    """Обновление записи техобслуживания"""
    maintenance_type: str | None = Field(None, min_length=2, max_length=100)
    performed_at: date | None = None
    issues_found: str | None = Field(None, max_length=1000)
    performed_by_id: UUID | None = None
    notes: str | None = Field(None, max_length=1000)


class AssetMaintenanceOutSchema(TimestampSchema):
    """Вывод записи техобслуживания"""
    id: UUID
    asset_id: UUID
    maintenance_type: str
    performed_at: date
    issues_found: str | None
    performed_by_id: UUID
    performed_by_name: str | None = None
    notes: str | None
