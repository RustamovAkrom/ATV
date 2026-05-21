from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class TopMetric(StrEnum):
    ASSIGNMENTS = "assignments"
    TRANSFERS = "transfers"
    REPAIRS = "repairs"


class TopAssetAnalyticsOut(BaseModel):
    asset_id: UUID
    asset_name: str
    assignment_count: int
    transfer_count: int
    repair_count: int
    primary_metric: TopMetric
    primary_value: int


class TopUserAnalyticsOut(BaseModel):
    user_id: UUID
    user_name: str
    email: str
    assignment_count: int
    transfer_count: int
    repair_count: int
    primary_metric: TopMetric
    primary_value: int


class TopServiceAnalyticsOut(BaseModel):
    service_id: UUID
    service_name: str
    assignment_count: int
    transfer_count: int
    repair_count: int
    primary_metric: TopMetric
    primary_value: int
