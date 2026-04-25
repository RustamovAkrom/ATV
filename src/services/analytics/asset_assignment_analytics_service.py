# services/analytics/asset_assignment_analytics_service.py

from decimal import Decimal
from uuid import UUID

from schemas.analytics.asset_assignment_analytics import (
    AssetAssignmentFilterInput,
    AssetAssignmentOut,
    AssetAssignmentPageOut,
    AssetAssignmentHistoryOut,
    AssignmentDurationMetrics,
    AssetAssignmentDetailOut,
    UserAssignmentSummary,
    AssetAssignmentTimeline,
    AssignmentTimelineEntry,
    AssignmentAggregates,
)
from schemas.pagination import PageOut, build_page

from schemas.pagination import PaginationParams
from core.security.auth.types import CurrentUser
from db.models.enums import UserRole
from repositories.analytics.asset_assignment_analytics_repo import (
    AssetAssignmentAnalyticsRepository,
)
from utils.helpers import utc_now


class AssetAssignmentAnalyticsService:
    """Service for assignment analytics."""

    def __init__(self, repo: AssetAssignmentAnalyticsRepository):
        self.repo = repo

    @staticmethod
    def _filter_email(email: str, current_user: CurrentUser) -> str:
        # Keep the response shape stable while avoiding broad exposure of user emails.
        if current_user.has_role(UserRole.ADMIN.value, UserRole.SUPERADMIN.value):
            return email
        return ""

    async def list_assignments(
        self,
        filters: AssetAssignmentFilterInput,
        pagination: PaginationParams,
        current_user: CurrentUser,
    ) -> AssetAssignmentPageOut:
        """List assignments with pagination."""
        assignments, total = await self.repo.list_assignments(filters, pagination)

        items = [
            AssetAssignmentDetailOut(
                id=a.id,
                asset_id=a.asset_id,
                asset_name=a.asset.name if a.asset else "Unknown",
                asset_tag=a.asset.asset_tag if a.asset else None,
                user_id=a.user_id,
                user_name=a.user.full_name if a.user else "Unknown",
                user_email=self._filter_email(a.user.email, current_user) if a.user else "",
                assigned_at=a.assigned_at,
                unassigned_at=a.unassigned_at,
                status="active" if a.unassigned_at is None else "inactive",
                duration_metrics=AssignmentDurationMetrics(
                    duration_days=self._calculate_duration_days(a.assigned_at, a.unassigned_at) or Decimal(0),
                    duration_formatted=self._format_duration(a.assigned_at, a.unassigned_at),
                    is_active=a.unassigned_at is None,
                ),
            )
            for a in assignments
        ]


        return build_page(
            schema=PageOut[AssetAssignmentDetailOut],
            items=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
            aggregates=None, # TODO
        )

    async def list_active_assignments(
        self,
        pagination: PaginationParams,
        current_user: CurrentUser,
    ) -> AssetAssignmentPageOut:
        """List currently active assignments."""
        assignments, total = await self.repo.list_active_assignments(pagination)

        items = [
            AssetAssignmentDetailOut(
                id=a.id,
                asset_id=a.asset_id,
                asset_name=a.asset.name if a.asset else "Unknown",
                asset_tag=a.asset.asset_tag if a.asset else None,
                user_id=a.user_id,
                user_name=a.user.full_name if a.user else "Unknown",
                user_email=self._filter_email(a.user.email, current_user) if a.user else "",
                assigned_at=a.assigned_at,
                unassigned_at=a.unassigned_at,
                status="active",
                duration_metrics=AssignmentDurationMetrics(
                    duration_days=self._calculate_duration_days(a.assigned_at, a.unassigned_at) or Decimal(0),
                    duration_formatted=self._format_duration(a.assigned_at, a.unassigned_at),
                    is_active=True,
                ),
            )
            for a in assignments
        ]

        return build_page(
            schema=PageOut[AssetAssignmentDetailOut],
            items=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
            aggregates=None, # TODO
        )

    async def get_assignment_with_duration(self, assignment_id: UUID) -> AssetAssignmentDetailOut | None:
        """Get single assignment with duration metrics."""
        # This would need to be implemented in repo if needed
        pass

    async def get_user_summary(self, user_id: UUID, current_user: CurrentUser) -> UserAssignmentSummary:
        """Get assignment summary for a user."""
        summary_dict = await self.repo.get_user_assignment_summary(user_id)
        summary_dict["user_email"] = self._filter_email(summary_dict["user_email"], current_user)

        return UserAssignmentSummary(**summary_dict)

    async def get_asset_timeline(self, asset_id: UUID, current_user: CurrentUser) -> AssetAssignmentTimeline:
        """Get assignment timeline for an asset."""
        assignments = await self.repo.get_assignment_timeline(asset_id)

        # Get asset info
        if assignments:
            asset = assignments[0].asset
        else:
            asset = None

        # Build timeline
        timeline_entries = [
            AssignmentTimelineEntry(
                sequence=i + 1,
                assigned_at=a.assigned_at,
                unassigned_at=a.unassigned_at,
                user_id=a.user_id,
                user_name=a.user.full_name if a.user else "Unknown",
                duration_days=self._calculate_duration_days(a.assigned_at, a.unassigned_at),
            )
            for i, a in enumerate(assignments)
        ]

        # Get current active assignment if any
        active_assignment = None
        for a in assignments:
            if a.unassigned_at is None:
                active_assignment = AssetAssignmentOut(
                    id=a.id,
                    asset_id=a.asset_id,
                    asset_name=asset.name if asset else "Unknown",
                    asset_tag=asset.asset_tag if asset else None,
                    user_id=a.user_id,
                    user_name=a.user.full_name if a.user else "Unknown",
                    user_email=self._filter_email(a.user.email, current_user) if a.user else "",
                    assigned_at=a.assigned_at,
                    unassigned_at=a.unassigned_at,
                    status="active",
                )
                break

        return AssetAssignmentTimeline(
            asset_id=asset_id,
            asset_name=asset.name if asset else "Unknown",
            total_assignments=len(assignments),
            active_assignment=active_assignment,
            timeline=timeline_entries,
        )

    async def get_aggregates(self, filters: AssetAssignmentFilterInput) -> AssignmentAggregates:
        """Get aggregated metrics."""
        agg_dict = await self.repo.get_aggregates(filters)

        # Get most assigned asset
        most_assigned = await self.repo.get_most_assigned_asset()
        if most_assigned:
            agg_dict["most_frequently_assigned_asset_id"] = most_assigned[0]
            agg_dict["most_frequently_assigned_asset_name"] = most_assigned[1]

        # Get most active user
        most_active = await self.repo.get_most_active_user()
        if most_active:
            agg_dict["most_active_user_id"] = most_active[0]
            agg_dict["most_active_user_name"] = most_active[1]

        return AssignmentAggregates(**agg_dict)

    @staticmethod
    def _calculate_duration_days(start, end) -> Decimal | None:
        """Calculate duration in days."""
        if end is None:
            return None
        duration = end - start
        return Decimal(duration.total_seconds() / 86400)

    @staticmethod
    def _format_duration(start, end) -> str:
        effective_end = end or utc_now()
        duration = effective_end - start
        total_hours = int(duration.total_seconds() // 3600)
        days, hours = divmod(total_hours, 24)
        return f"{days}d {hours}h"
