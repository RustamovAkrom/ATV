from enum import StrEnum
from uuid import UUID

from schemas.base import BaseResponseSchema


class TopMetric(StrEnum):
    ASSIGNMENTS = "assignments"
    TRANSFERS = "transfers"
    REPAIRS = "repairs"


class TopAssetAnalyticsOut(BaseResponseSchema):
    asset_id: UUID
    asset_name: str
    assignment_count: int
    transfer_count: int
    repair_count: int
    primary_metric: TopMetric
    primary_value: int


class TopUserAnalyticsOut(BaseResponseSchema):
    user_id: UUID
    user_name: str
    email: str
    assignment_count: int
    transfer_count: int
    repair_count: int
    primary_metric: TopMetric
    primary_value: int


class TopServiceAnalyticsOut(BaseResponseSchema):
    service_id: UUID
    service_name: str
    assignment_count: int
    transfer_count: int
    repair_count: int
    primary_metric: TopMetric
    primary_value: int
