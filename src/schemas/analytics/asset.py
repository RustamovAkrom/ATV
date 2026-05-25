from __future__ import annotations

from schemas.analytics.common import DistributionSchema
from schemas.base import BaseSchema


class RegionGeoMetricSchema(BaseSchema):
    region_id: str
    region_name: str
    metrics: dict[str, int]


class AssetDistributionDataSchema(BaseSchema):
    total_assets: int
    by_region: DistributionSchema
    by_service: DistributionSchema
    by_warehouse: DistributionSchema
    by_status: DistributionSchema
    geo: list[RegionGeoMetricSchema]


class AssetLifecycleDataSchema(BaseSchema):
    lifecycle_distribution: DistributionSchema
    critical_assets_percentage: float
