from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from db.models.enums import AssetStatus
from schemas.assets.asset_maintenance import AssetMaintenanceOutSchema
from schemas.base import BaseRequestSchema, BaseSchema, NamedRefSchema, TimestampSchema
from schemas.pagination import PageOutSchema


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


class DepartmentRef(NamedRefSchema):
    pass


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


class AssetCreate(BaseRequestSchema):
    name: str = Field(min_length=1, max_length=255)
    model_id: UUID

    class_id: UUID | None = None
    department_id: UUID | None = None
    region_id: UUID | None = None
    service_id: UUID | None = None

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

    assign_to_self: bool = Field(
        default=False, description="Назначить актив текущему пользователю"
    )


class AssetUpdate(BaseRequestSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)

    model_id: UUID | None = None
    class_id: UUID | None = None
    department_id: UUID | None = None

    region_id: UUID | None = None
    service_id: UUID | None = None
    owner_id: UUID | None = None

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


class AssetAssignRequest(BaseRequestSchema):
    user_id: UUID


class AssetStatusChangeRequest(BaseRequestSchema):
    status: AssetStatus


class AssetFilters(BaseRequestSchema):
    owner_id: UUID | None = None
    department_id: UUID | None = None
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
    status: AssetStatus
    serial_number: str | None = None
    model: AssetRef
    asset_class: AssetRef | None = None
    owner: UserRef | None = None
    department: DepartmentRef | None = None
    region: RegionRef | None = None
    service: ServiceRef | None = None
    warehouse: WarehouseRef | None = None
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
    maintenances: list[AssetMaintenanceOutSchema] = Field(default_factory=list)


AssetPage = PageOutSchema[AssetSchema]
