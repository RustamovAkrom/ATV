"""Expense schemas for validation and API responses."""

from datetime import datetime
from uuid import UUID

from pydantic import ConfigDict, Field

from db.models.enums import ExpenseTypeEnum
from schemas.base import BaseSchema, NamedRefSchema

AssetRef = NamedRefSchema
RegionRef = NamedRefSchema
ServiceRef = NamedRefSchema


class ExpenseCreateSchema(BaseSchema):
    amount: float = Field(..., gt=0, le=1e12, description="Amount must be positive")
    currency: str = Field("UZS", min_length=3, max_length=10, pattern=r"^[A-Z]{3}$")
    expense_type: ExpenseTypeEnum
    description: str | None = Field(None, max_length=1000)
    asset_id: UUID | None = None
    repair_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None
    occurred_at: datetime | None = None
    file_url: str | None = Field(None, max_length=2048)


class ExpenseUpdateSchema(BaseSchema):
    amount: float | None = Field(None, gt=0)
    currency: str | None = Field(None, min_length=3, max_length=10)
    expense_type: ExpenseTypeEnum | None = None
    description: str | None = Field(None, max_length=1000)
    file_url: str | None = Field(None, max_length=2048)


class ExpenseOutSchema(BaseSchema):
    id: UUID
    amount: float
    currency: str
    expense_type: ExpenseTypeEnum = Field(..., alias="expense_type_code")
    description: str | None
    file_url: str | None
    asset: AssetRef | None = None
    repair_id: UUID | None = None
    region: RegionRef | None = None
    service: ServiceRef | None = None
    created_by_id: UUID | None = None
    created_by_name: str | None = None
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime


class ExpensePageSchema(BaseSchema):
    """Paginated expenses response."""

    total: int
    page: int
    size: int
    items: list[ExpenseOutSchema]

    model_config = ConfigDict(from_attributes=True)


class ExpenseStatsSchema(BaseSchema):
    """Statistics about expenses."""

    total_amount: float
    total_count: int
    by_type: dict[str, float]
    by_region: dict[str, float]
    by_service: dict[str, float]

    model_config = ConfigDict(from_attributes=True)
