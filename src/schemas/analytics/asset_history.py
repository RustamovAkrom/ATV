# schemas/analytics/asset_history.py

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.v1.analytics._utils import sanitize_search


class AssetHistoryFilter(BaseModel):
    asset_id: UUID | None = None
    user_id: UUID | None = None
    action: str | None = Field(default=None, max_length=50)
    date_from: datetime | None = None
    date_to: datetime | None = None
    search: str | None = Field(
        None, description="Search by asset name/tag or user name", max_length=100
    )

    @field_validator("action", "search")
    @classmethod
    def normalize_text_filters(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = sanitize_search(value)
        return cleaned or None


class AssetHistoryOut(BaseModel):
    id: UUID
    asset_id: UUID
    asset_name: str
    user_id: UUID
    user_name: str
    action: str
    description: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetHistoryMetrics(BaseModel):
    """Metrics aggregated for asset history."""

    action: str
    count: int
    last_occurrence: datetime
    first_occurrence: datetime


class AssetHistoryAggregates(BaseModel):
    """Aggregated history data."""

    total_entries: int
    unique_assets: int
    unique_users: int
    date_range_start: datetime | None
    date_range_end: datetime | None
    actions_breakdown: list[AssetHistoryMetrics]
    most_active_asset_id: UUID | None
    most_active_asset_name: str | None
    most_active_user_id: UUID | None
    most_active_user_name: str | None


class AssetHistoryPage(BaseModel):
    """Paginated history with total count."""

    items: list[AssetHistoryOut]
    total: int
    page: int
    limit: int
