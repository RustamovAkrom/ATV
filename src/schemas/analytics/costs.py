from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RepairCostAnalyticsOut(BaseModel):
    repair_id: UUID
    asset_id: UUID
    asset_name: str
    reported_at: datetime
    labor_cost: float
    parts_cost: float
    total_cost: float


class AssetCostAnalyticsOut(BaseModel):
    asset_id: UUID
    asset_name: str
    asset_tag: str | None = None
    purchase_cost: float
    repair_cost: float
    total_cost: float


class RegionCostAnalyticsOut(BaseModel):
    region_id: UUID
    region_name: str
    purchase_cost: float
    repair_cost: float
    total_cost: float
