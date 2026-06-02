
from schemas.analytics.common import TimeSeriesSchema
from schemas.base import BaseResponseSchema


class TransferAssetMetricSchema(BaseResponseSchema):
    asset_id: str
    asset_name: str
    transfer_count: int

class TransferAnalyticsDataSchema(BaseResponseSchema):
    transfers_per_period: TimeSeriesSchema
    most_moved_assets: list[TransferAssetMetricSchema]
    unstable_assets: list[TransferAssetMetricSchema]
