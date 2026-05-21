# schemas/analytics/asset_assignment_analytics.py

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.v1.analytics._utils import sanitize_search


class AssignmentAnalyticsStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class AssetAssignmentFilterInput(BaseModel):
    """Filters for asset assignment analytics queries."""

    asset_id: UUID | None = None
    user_id: UUID | None = None
    status: AssignmentAnalyticsStatus | None = Field(
        None, description="active or inactive"
    )
    date_from: datetime | None = None
    date_to: datetime | None = None
    search: str | None = Field(
        None, description="Search by asset name/tag or user name", max_length=100
    )

    @field_validator("search")
    @classmethod
    def normalize_search(cls, value: str | None) -> str | None:
        cleaned = sanitize_search(value)
        return cleaned or None


class AssetAssignmentOut(BaseModel):
    """Single assignment record."""

    id: UUID
    asset_id: UUID
    asset_name: str
    user_id: UUID
    user_name: str
    user_email: str
    assigned_at: datetime
    unassigned_at: datetime | None
    status: str  # "active" or "inactive"

    model_config = ConfigDict(from_attributes=True)


class AssignmentDurationMetrics(BaseModel):
    """Duration metrics for an assignment."""

    duration_days: Decimal
    duration_formatted: str  # "12 days, 5 hours"
    is_active: bool


class AssetAssignmentDetailOut(AssetAssignmentOut):
    """Assignment with duration metrics."""

    duration_metrics: AssignmentDurationMetrics


class UserAssignmentSummary(BaseModel):
    """Summary of assignments for a user."""

    user_id: UUID
    user_name: str
    user_email: str
    active_assignments_count: int
    total_assignments_count: int
    average_duration_days: Decimal | None
    longest_assignment_days: Decimal | None
    recent_assignment_date: datetime | None


class AssetAssignmentHistoryOut(BaseModel):
    """Assignment history with duration."""

    assignment_id: UUID
    asset_id: UUID
    asset_name: str
    user_id: UUID
    user_name: str
    assigned_at: datetime
    unassigned_at: datetime | None
    duration_days: Decimal | None
    status: str


class AssignmentTimelineEntry(BaseModel):
    """Timeline entry for a single asset."""

    sequence: int
    assigned_at: datetime
    unassigned_at: datetime | None
    user_id: UUID
    user_name: str
    duration_days: Decimal | None


class AssetAssignmentTimeline(BaseModel):
    """Complete timeline for an asset's assignments."""

    asset_id: UUID
    asset_name: str
    total_assignments: int
    active_assignment: AssetAssignmentOut | None
    timeline: list[AssignmentTimelineEntry]


class AssignmentAggregates(BaseModel):
    """Aggregated metrics for assignments."""

    total_active_assignments: int
    total_inactive_assignments: int
    total_assignments: int
    average_assignment_duration_days: Decimal | None
    longest_assignment_duration_days: Decimal | None
    most_frequently_assigned_asset_id: UUID | None
    most_frequently_assigned_asset_name: str | None
    most_active_user_id: UUID | None
    most_active_user_name: str | None


class AssignmentPageOut(BaseModel):
    """Paginated assignment list."""

    items: list[AssetAssignmentOut]
    total: int
    page: int
    limit: int


class AssetAssignmentPageOut(BaseModel):
    """
    Paginated response for assignment analytics.
    Includes list + aggregates for dashboards.
    """

    items: list[AssetAssignmentDetailOut]

    # pagination
    total: int
    page: int
    limit: int
    pages: int

    # analytics
    aggregates: AssignmentAggregates | None = None

    # optional meta for frontend flexibility
    has_next: bool
    has_prev: bool
