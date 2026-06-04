from datetime import datetime
from enum import StrEnum

from schemas.base import BaseResponseSchema


class TrendInterval(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendPointOut(BaseResponseSchema):
    bucket_start: datetime
    bucket_end: datetime
    value: int


class RepairTrendPointOut(TrendPointOut):
    total_cost: float


class TrendSeriesOut(BaseResponseSchema):
    interval: TrendInterval
    points: list[TrendPointOut]


class RepairTrendSeriesOut(BaseResponseSchema):
    interval: TrendInterval
    points: list[RepairTrendPointOut]
