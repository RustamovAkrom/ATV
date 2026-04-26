from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from db.models.enums import RepairStatus


class RepairPartCreate(BaseModel):
    part_name: str = Field(min_length=1, max_length=150)
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)


class RepairReportRequest(BaseModel):
    description: str | None = Field(default=None, max_length=500)


class RepairStartRequest(BaseModel):
    assigned_to_id: UUID | None = None
    description: str | None = Field(default=None, max_length=500)
    labor_cost: Decimal | None = Field(default=None, ge=0)
    parts: list[RepairPartCreate] = Field(default_factory=list)


class RepairCompleteRequest(BaseModel):
    labor_cost: Decimal | None = Field(default=None, ge=0)
    parts: list[RepairPartCreate] = Field(default_factory=list)


class RepairCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


class RepairPartSchema(BaseModel):
    id: UUID
    part_name: str
    quantity: int
    unit_price: Decimal | None

    model_config = ConfigDict(from_attributes=True)


class RepairSchema(BaseModel):
    id: UUID
    asset_id: UUID
    reported_by_id: UUID | None
    assigned_to_id: UUID | None
    description: str | None
    status: RepairStatus
    started_at: datetime | None
    completed_at: datetime | None
    labor_cost: Decimal | None
    total_cost: Decimal
    parts: list[RepairPartSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
