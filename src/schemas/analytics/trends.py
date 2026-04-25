from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class TrendInterval(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class TrendPointOut(BaseModel):
    bucket_start: datetime
    bucket_end: datetime
    value: int


class RepairTrendPointOut(TrendPointOut):
    total_cost: float


class TrendSeriesOut(BaseModel):
    interval: TrendInterval
    points: list[TrendPointOut]


class RepairTrendSeriesOut(BaseModel):
    interval: TrendInterval
    points: list[RepairTrendPointOut]
