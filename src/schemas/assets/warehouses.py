from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema


class WarehouseMoveRequest(BaseSchema):
    warehouse_id: UUID


class WarehouseCreateSchema(BaseSchema):
    name: str = Field(min_length=2, max_length=150)
    code: str | None = Field(None, max_length=50)
    region_id: UUID
    service_id: UUID | None = None
    manager_user_id: UUID | None = None
    is_active: bool = True


class WarehouseUpdateSchema(BaseSchema):
    name: str = Field(min_length=2, max_length=150)
    code: str = Field(min_length=2, max_length=150)
    region_id: UUID | None = None
    service_id: UUID | None = None
    manager_user_id: UUID | None = None
    is_active: bool | None = None


class WareehouseOutSchema(TimestampSchema):
    id: UUID
    name: str
    code: str | None
    region_id: UUID
    service_id: UUID | None
    manager_user_id: UUID | None
    is_active: bool
