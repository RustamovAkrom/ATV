from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AnalyticsFilters(BaseModel):
    region_id: UUID | None = None
    service_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None


class AggregationResultSchema(BaseModel):
    key: str
    label: str
    count: int
    percentage: float


class DistributionSchema(BaseModel):
    labels: list[str]
    values: list[int]
    items: list[AggregationResultSchema] = Field(default_factory=list)


class TimeSeriesPointSchema(BaseModel):
    period: date
    value: int | float


class TimeSeriesSchema(BaseModel):
    labels: list[str]
    values: list[int | float]
    points: list[TimeSeriesPointSchema] = Field(default_factory=list)


class KPIResponseSchema(BaseModel):
    key: str
    label: str
    value: int | float
    unit: str | None = None


class AnalyticsMetaSchema(BaseModel):
    generated_at: datetime
    filters: AnalyticsFilters


class AnalyticsResponseSchema(BaseModel):
    data: dict[str, Any]
    meta: AnalyticsMetaSchema
