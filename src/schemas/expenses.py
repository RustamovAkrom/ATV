"""Expense schemas for validation and API responses."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExpenseTypeEnum(str, Enum):
    """Supported expense types."""

    PURCHASE = "purchase"
    REPAIR = "repair"
    MAINTENANCE = "maintenance"
    LOGISTICS = "logistics"
    OTHER = "other"


class AssetRef(BaseModel):
    """Reference to an asset."""

    id: UUID
    asset_tag: str


class UserRef(BaseModel):
    """Reference to a user."""

    id: UUID
    full_name: str


class RegionRef(BaseModel):
    """Reference to a region."""

    id: UUID
    name: str


class ServiceRef(BaseModel):
    """Reference to a service."""

    id: UUID
    name: str


class ExpenseCreateSchema(BaseModel):
    """Schema for creating an expense."""

    amount: float = Field(..., gt=0, description="Amount must be positive")
    currency: str = Field(default="UZS", min_length=3, max_length=10)
    expense_type: ExpenseTypeEnum = Field(...)
    description: str | None = Field(None, max_length=1000)
    asset_id: UUID | None = None
    repair_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None
    occurred_at: datetime | None = None
    file_url: str | None = Field(None, max_length=2048)

    model_config = ConfigDict(from_attributes=True)


class ExpenseUpdateSchema(BaseModel):
    """Schema for updating an expense."""

    amount: float | None = Field(None, gt=0)
    currency: str | None = None
    expense_type: ExpenseTypeEnum | None = None
    description: str | None = None
    file_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ExpenseOutSchema(BaseModel):
    """Schema for expense output/response."""

    id: UUID
    amount: float
    currency: str
    expense_type: ExpenseTypeEnum = Field(..., alias="expense_type_code")
    description: str | None
    file_url: str | None

    # References
    asset: AssetRef | None = None
    repair_id: UUID | None = None
    region: RegionRef | None = None
    service: ServiceRef | None = None
    created_by: UserRef | None = None

    # Timestamps
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True, populate_by_name=True, use_enum_values=True
    )


class ExpensePageSchema(BaseModel):
    """Paginated expenses response."""

    total: int
    page: int
    size: int
    items: list[ExpenseOutSchema]

    model_config = ConfigDict(from_attributes=True)


class ExpenseStatsSchema(BaseModel):
    """Statistics about expenses."""

    total_amount: float
    total_count: int
    by_type: dict[str, float]
    by_region: dict[str, float]
    by_service: dict[str, float]

    model_config = ConfigDict(from_attributes=True)
