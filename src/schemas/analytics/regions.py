from datetime import datetime
from uuid import UUID

from schemas.base import BaseResponseSchema


class RegionAssetStatusCounts(BaseResponseSchema):
    active: int
    assigned: int
    in_repair: int
    archived: int
    total: int


class RegionOverviewOut(BaseResponseSchema):
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


class RegionServiceLoadOut(BaseResponseSchema):
    service_id: UUID
    service_name: str
    asset_count: int
    active_assignments: int
    repairs_count: int


class RegionAssetCostSummaryOut(BaseResponseSchema):
    asset_id: UUID
    asset_name: str
    purchase_cost: float
    repair_cost: float
    total_cost: float


class RegionDetailsOut(RegionOverviewOut):
    services: list[RegionServiceLoadOut]
    top_cost_assets: list[RegionAssetCostSummaryOut]


class RegionHeatmapPointOut(BaseResponseSchema):
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
