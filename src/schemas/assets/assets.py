from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import ConfigDict, Field

from db.models.enums import AssetStatus
from schemas.pagination import PageOutSchema
from schemas.base import BaseSchema, TimestampSchema


class AssetRef(BaseSchema):
    id: UUID
    name: str


class UserRef(BaseSchema):
    id: UUID
    login: str


class RegionRef(BaseSchema):
    id: UUID
    name: str


class ServiceRef(BaseSchema):
    id: UUID
    name: str


class WarehouseRef(BaseSchema):
    id: UUID
    name: str


class AssetAssignmentSchema(BaseSchema):
    id: UUID
    user: UserRef
    assigned_at: datetime
    unassigned_at: datetime | None


class AssetHistorySchema(BaseSchema):
    id: UUID
    action: str
    description: str
    created_at: datetime
    user: UserRef


class AssetCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=100)
    model_id: UUID

    class_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None
    owner_id: UUID | None = None

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


class AssetUpdate(BaseSchema):
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


class AssetAssignRequest(BaseSchema):
    user_id: UUID


class AssetStatusChangeRequest(BaseSchema):
    status: AssetStatus


class AssetFilters(BaseSchema):
    owner_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None
    class_id: UUID | None = None

    manufacturer_id: UUID | None = None
    category_id: UUID | None = None

    status: AssetStatus | None = None

    search: str | None = Field(default=None, max_length=251005)


class AssetSchema(TimestampSchema):
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
    assignments: list[AssetAssignmentSchema] = Field(default_factory=list)
    metadata: dict = Field(alias="meta")
    condition_percent: int
    commission_date: date | None
    warranty_end: date | None
    purchase_date: date | None
    purchase_cost: Decimal | None
    last_repair_date: date | None
    failure_count: int
    usage_intensity: int


class AssetDetailSchema(AssetSchema):
    assignments: list[AssetAssignmentSchema] = Field(default_factory=list)
    history_entries: list[AssetHistorySchema] = Field(default_factory=list)


AssetPage = PageOutSchema[AssetSchema]
