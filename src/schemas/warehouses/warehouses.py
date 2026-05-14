from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema


class WarehouseMoveRequest(BaseSchema):
    """Запрос на перемещение актива на склад"""
    warehouse_id: UUID = Field(..., description="ID целевого склада")


class WarehouseCreateSchema(BaseSchema):
    """Создание нового склада"""
    name: str = Field(min_length=2, max_length=150, description="Название склада")
    code: str | None = Field(None, max_length=50, description="Код склада (уникальный)")
    region_id: UUID = Field(..., description="ID региона")
    service_id: UUID | None = Field(None, description="ID сервиса")
    manager_user_id: UUID | None = Field(None, description="ID ответственного пользователя")
    is_active: bool = Field(True, description="Активен ли склад")


class WarehouseUpdateSchema(BaseSchema):
    """Обновление склада"""
    name: str | None = Field(None, min_length=2, max_length=150, description="Название склада")  # <-- исправлено: optional
    code: str | None = Field(None, min_length=2, max_length=150, description="Код склада")  # <-- исправлено: optional
    region_id: UUID | None = Field(None, description="ID региона")
    service_id: UUID | None = Field(None, description="ID сервиса")
    manager_user_id: UUID | None = Field(None, description="ID ответственного пользователя")
    is_active: bool | None = Field(None, description="Активен ли склад")


class WarehouseOutSchema(TimestampSchema):  # <-- исправлено: WareehouseOutSchema → WarehouseOutSchema
    """Вывод информации о складе"""
    id: UUID
    name: str
    code: str | None
    region_id: UUID
    service_id: UUID | None
    manager_user_id: UUID | None
    is_active: bool
