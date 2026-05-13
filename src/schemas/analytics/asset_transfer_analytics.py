# schemas/analytics/asset_transfer_analytics.py

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import ConfigDict, Field, field_validator
from schemas.base import BaseSchema
from api.v1.analytics._utils import sanitize_search
from db.models.enums import TransferStatus


class AssetTransferFilterInput(BaseSchema):
    """Filters for asset transfer analytics queries."""

    asset_id: UUID | None = None
    created_by_id: UUID | None = None
    received_by_id: UUID | None = None
    from_warehouse_id: UUID | None = None
    to_warehouse_id: UUID | None = None
    from_service_id: UUID | None = None
    to_service_id: UUID | None = None
    status: TransferStatus | None = Field(
        None, description="pending, completed, or cancelled"
    )
    date_from: datetime | None = None
    date_to: datetime | None = None
    search: str | None = Field(
        None, description="Search by asset name/tag", max_length=100
    )

    @field_validator("search")
    @classmethod
    def normalize_search(cls, value: str | None) -> str | None:
        cleaned = sanitize_search(value)
        return cleaned or None


class AssetTransferOut(BaseSchema):
    """Transfer record with location details."""

    id: UUID
    asset_id: UUID
    asset_name: str
    asset_tag: str | None
    status: str

    from_warehouse_name: str | None
    to_warehouse_name: str | None
    from_service_name: str | None
    to_service_name: str | None

    created_by_id: UUID
    created_by_name: str
    created_at: datetime

    received_by_id: UUID | None
    received_by_name: str | None
    transferred_at: datetime | None

    comment: str | None


class AssetTransferPageOut(BaseSchema):
    items: list[AssetTransferOut]

    total: int
    page: int
    limit: int
    pages: int

    has_next: bool
    has_prev: bool


class TransferDurationMetrics(BaseSchema):
    """Duration metrics for a transfer."""

    pending_duration_days: Decimal | None
    pending_duration_formatted: str | None
    total_duration_days: Decimal | None
    total_duration_formatted: str | None
    days_to_completion: Decimal | None  # Transfer time after approval
    is_pending: bool


class AssetTransferDetailOut(AssetTransferOut):
    """Transfer with duration metrics."""

    duration_metrics: TransferDurationMetrics


class TransferHistoryEntry(BaseSchema):
    """Transfer history entry for an asset."""

    transfer_id: UUID
    sequence: int
    status: str
    from_location: str | None  # warehouse or service
    to_location: str | None
    created_at: datetime
    transferred_at: datetime | None
    created_by_name: str
    duration_days: Decimal | None


class AssetTransferHistory(BaseSchema):
    """Complete transfer history for an asset."""

    asset_id: UUID
    asset_name: str
    total_transfers: int
    completed_transfers: int
    pending_transfers: int
    cancelled_transfers: int
    history: list[TransferHistoryEntry]


class TransferStatusBreakdown(BaseSchema):
    """Breakdown of transfers by status."""

    status: str
    count: int
    percentage: Decimal
    average_pending_days: Decimal | None  # Only for pending transfers


class TransferBottleneck(BaseSchema):
    """Bottleneck analysis - transfers waiting too long."""

    transfer_id: UUID
    asset_name: str
    asset_tag: str | None
    status: str
    pending_days: int
    created_by_name: str
    from_location: str | None
    to_location: str | None
    created_at: datetime


class TransferMetrics(BaseSchema):
    """Aggregated transfer metrics."""

    total_transfers: int
    completed_transfers: int
    pending_transfers: int
    cancelled_transfers: int

    average_completion_time_days: Decimal | None
    longest_completion_time_days: Decimal | None
    shortest_completion_time_days: Decimal | None

    # Bottleneck indicators
    oldest_pending_transfer_days: int | None
    oldest_pending_transfer_id: UUID | None
    transfers_pending_over_7_days: int
    transfers_pending_over_30_days: int

    # Timeline data
    status_breakdown: list[TransferStatusBreakdown]


class WarehouseTransferMetrics(BaseSchema):
    """Transfer metrics per warehouse."""

    warehouse_id: UUID
    warehouse_name: str
    transfers_from: int
    transfers_to: int
    pending_in: int
    pending_out: int
    average_duration_days: Decimal | None


class TransferPageOut(BaseSchema):
    """Paginated transfer list."""

    items: list[AssetTransferOut]
    total: int
    page: int
    limit: int


class BottleneckReportOut(BaseSchema):
    """Report of transfer bottlenecks."""

    total_bottlenecks: int
    critical_bottlenecks: list[TransferBottleneck]  # pending > 30 days
    warning_bottlenecks: list[TransferBottleneck]  # pending > 7 days
