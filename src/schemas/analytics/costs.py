from datetime import datetime
from uuid import UUID
from schemas.base import BaseSchema


class RepairCostAnalyticsOut(BaseSchema):
    repair_id: UUID
    asset_id: UUID
    asset_name: str
    reported_at: datetime
    labor_cost: float
    parts_cost: float
    total_cost: float


class AssetCostAnalyticsOut(BaseSchema):
    asset_id: UUID
    asset_name: str
    asset_tag: str | None = None
    purchase_cost: float
    repair_cost: float
    total_cost: float


class RegionCostAnalyticsOut(BaseSchema):
    region_id: UUID
    region_name: str
    purchase_cost: float
    repair_cost: float
    total_cost: float
