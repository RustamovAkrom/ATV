from pydantic import BaseModel


class RepairAssetMetricSchema(BaseModel):
    asset_id: str
    asset_name: str
    repair_count: int
    total_repair_cost: float


class RepairAnalyticsDataSchema(BaseModel):
    average_repair_cost: float
    per_asset: list[RepairAssetMetricSchema]
    abnormal_repair_frequency_assets: list[RepairAssetMetricSchema]
