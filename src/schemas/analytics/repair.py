from schemas.base import BaseResponseSchema


class RepairAssetMetricSchema(BaseResponseSchema):
    asset_id: str
    asset_name: str
    repair_count: int
    total_repair_cost: float


class RepairAnalyticsDataSchema(BaseResponseSchema):
    average_repair_cost: float
    per_asset: list[RepairAssetMetricSchema]
    abnormal_repair_frequency_assets: list[RepairAssetMetricSchema]
