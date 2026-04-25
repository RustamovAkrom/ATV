from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class AssignmentMetricsCard(BaseModel):
    total_active: int
    total_inactive: int
    average_duration_days: Decimal | None


class TransferMetricsCard(BaseModel):
    total_pending: int
    total_completed: int
    average_completion_days: Decimal | None
    critical_bottlenecks: int


class AssetHistoryMetricsCard(BaseModel):
    total_history_entries: int
    most_active_asset_id: UUID | None
    most_active_asset_name: str | None
    last_history_entry_date: datetime | None


class DashboardOverviewOut(BaseModel):
    timestamp: datetime
    period: str

    assignment_metrics: AssignmentMetricsCard
    transfer_metrics: TransferMetricsCard
    asset_history_metrics: AssetHistoryMetricsCard

    total_assets_with_active_assignments: int
    total_users_with_active_assignments: int
    total_assets_in_transfer: int
