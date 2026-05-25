from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from schemas.base import BaseSchema


class AnalyticsFilters(BaseSchema):
    region_id: UUID | None = None
    service_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None


class AggregationResultSchema(BaseSchema):
    key: str
    label: str
    count: int
    percentage: float


class DistributionSchema(BaseSchema):
    labels: list[str]
    values: list[int]
    items: list[AggregationResultSchema] = Field(default_factory=list)


class TimeSeriesPointSchema(BaseSchema):
    period: date
    value: int | float


class TimeSeriesSchema(BaseSchema):
    labels: list[str]
    values: list[int | float]
    points: list[TimeSeriesPointSchema] = Field(default_factory=list)


class KPIResponseSchema(BaseSchema):
    key: str
    label: str
    value: int | float
    unit: str | None = None


class AnalyticsMetaSchema(BaseSchema):
    generated_at: datetime
    filters: AnalyticsFilters


class AnalyticsResponseSchema(BaseSchema):
    data: dict[str, Any]
    meta: AnalyticsMetaSchema
