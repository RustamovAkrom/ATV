from __future__ import annotations

from pydantic import BaseModel

from schemas.analytics.common import DistributionSchema


class RegionGeoMetricSchema(BaseModel):
    region_id: str
    region_name: str
    metrics: dict[str, int]


class AssetDistributionDataSchema(BaseModel):
    total_assets: int
    by_region: DistributionSchema
    by_service: DistributionSchema
    by_warehouse: DistributionSchema
    by_status: DistributionSchema
    geo: list[RegionGeoMetricSchema]


class AssetLifecycleDataSchema(BaseModel):
    lifecycle_distribution: DistributionSchema
    critical_assets_percentage: float
