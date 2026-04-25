from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from db.models.enums import AssetStatus
from schemas.pagination import PageSchema


class AssetRef(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserRef(BaseModel):
    id: UUID
    login: str

    model_config = ConfigDict(from_attributes=True)


class RegionRef(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class ServiceRef(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class WarehouseRef(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class AssetAssignmentSchema(BaseModel):
    id: UUID
    user: UserRef
    assigned_at: datetime
    unassigned_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class AssetHistorySchema(BaseModel):
    id: UUID
    action: str
    description: str
    created_at: datetime
    user: UserRef

    model_config = ConfigDict(from_attributes=True)


class AssetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=100)
    model_id: UUID
    owner_id: UUID | None = None
    class_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None
    asset_tag: str | None = Field(default=None, max_length=255)
    serial_number: str | None = Field(default=None, max_length=255)
    commission_date: date | None = None
    warranty_end: date | None = None
    condition_percent: int = Field(default=100, ge=0, le=100)
    purchase_date: date | None = None
    purchase_cost: Decimal | None = Field(default=None, ge=0)
    last_repair_date: date | None = None
    failure_count: int = Field(default=0, ge=0)
    usage_intensity: int = Field(default=0, ge=0)
    metadata: dict = Field(default_factory=dict)


class AssetUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: str | None = Field(default=None, min_length=1, max_length=100)
    model_id: UUID | None = None
    class_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None
    asset_tag: str | None = Field(default=None, max_length=255)
    serial_number: str | None = Field(default=None, max_length=255)
    commission_date: date | None = None
    warranty_end: date | None = None
    condition_percent: int | None = Field(default=None, ge=0, le=100)
    purchase_date: date | None = None
    purchase_cost: Decimal | None = Field(default=None, ge=0)
    last_repair_date: date | None = None
    failure_count: int | None = Field(default=None, ge=0)
    usage_intensity: int | None = Field(default=None, ge=0)
    metadata: dict | None = None


class AssetAssignRequest(BaseModel):
    user_id: UUID


class AssetStatusChangeRequest(BaseModel):
    status: AssetStatus


class AssetFilters(BaseModel):
    owner_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None
    class_id: UUID | None = None

    manufacturer_id: UUID | None = None
    category_id: UUID | None = None

    status: AssetStatus | None = None
    search: str | None = Field(default=None, max_length=255)


class AssetSchema(BaseModel):
    id: UUID
    name: str
    type: str
    status: AssetStatus
    asset_tag: str | None
    serial_number: str | None
    model: AssetRef
    asset_class: AssetRef | None
    owner: UserRef | None
    region: RegionRef | None
    service: ServiceRef | None
    warehouse: WarehouseRef | None
    metadata: dict = Field(alias="meta")
    condition_percent: int
    commission_date: date | None
    warranty_end: date | None
    purchase_date: date | None
    purchase_cost: Decimal | None
    last_repair_date: date | None
    failure_count: int
    usage_intensity: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AssetDetailSchema(AssetSchema):
    assignments: list[AssetAssignmentSchema] = Field(default_factory=list)
    history_entries: list[AssetHistorySchema] = Field(default_factory=list)


AssetPage = PageSchema[AssetSchema]
