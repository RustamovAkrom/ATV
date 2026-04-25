from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RegionAssetStatusCounts(BaseModel):
    active: int
    assigned: int
    in_repair: int
    archived: int
    total: int


class RegionOverviewOut(BaseModel):
    region_id: UUID
    region_name: str
    latitude: float | None = None
    longitude: float | None = None
    geojson: dict | None = None
    asset_counts: RegionAssetStatusCounts
    transfers_in: int
    transfers_out: int
    repairs_count: int
    assignment_load: int


class RegionServiceLoadOut(BaseModel):
    service_id: UUID
    service_name: str
    asset_count: int
    active_assignments: int
    repairs_count: int


class RegionAssetCostSummaryOut(BaseModel):
    asset_id: UUID
    asset_name: str
    asset_tag: str | None = None
    purchase_cost: float
    repair_cost: float
    total_cost: float


class RegionDetailsOut(RegionOverviewOut):
    services: list[RegionServiceLoadOut]
    top_cost_assets: list[RegionAssetCostSummaryOut]


class RegionHeatmapPointOut(BaseModel):
    region_id: UUID
    region_name: str
    latitude: float | None = None
    longitude: float | None = None
    geojson: dict | None = None
    score: float
    asset_total: int
    active_assignments: int
    repairs_count: int
    transfers_in: int
    transfers_out: int
    updated_at: datetime
