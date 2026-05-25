from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import Field, computed_field

from schemas.base import BaseSchema

T = TypeVar("T")


class AnalyticsFilters(BaseSchema):
    """Базовые фильтры для аналитики"""

    region_id: UUID | None = None
    service_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


class AnalyticsPageOut(BaseSchema, Generic[T]):
    """Универсальная пагинация для аналитики"""

    items: list[T]
    total: int
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    @computed_field
    @property
    def pages(self) -> int:
        from math import ceil

        return ceil(self.total / self.limit) if self.total > 0 else 1

    @computed_field
    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        return self.page > 1


class DurationMetrics(BaseSchema):
    """Метрики длительности"""

    duration_days: Decimal | None
    duration_formatted: str | None


class TransferDurationMetrics(DurationMetrics):
    """Метрики для трансферов"""

    pending_duration_days: Decimal | None
    pending_duration_formatted: str | None
    total_duration_days: Decimal | None
    total_duration_formatted: str | None
    days_to_completion: Decimal | None
    is_pending: bool
