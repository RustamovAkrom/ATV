from pydantic import BaseModel

from schemas.analytics.common import TimeSeriesSchema


class TransferAssetMetricSchema(BaseModel):
    asset_id: str
    asset_name: str
    transfer_count: int


class TransferAnalyticsDataSchema(BaseModel):
    transfers_per_period: TimeSeriesSchema
    most_moved_assets: list[TransferAssetMetricSchema]
    unstable_assets: list[TransferAssetMetricSchema]
