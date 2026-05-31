from decimal import Decimal
from uuid import UUID

from repositories.analytics.asset_assignment_analytics_repo import (
    AssetAssignmentAnalyticsRepository,
)
from schemas.analytics.asset_assignment_analytics import (
    AssetAssignmentDetailOut,
    AssetAssignmentFilterInput,
    AssetAssignmentOut,
    AssetAssignmentTimeline,
    AssignmentAggregates,
    AssignmentDurationMetrics,
    AssignmentTimelineEntry,
    UserAssignmentSummary,
)
from schemas.auth import CurrentUserSchema
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class AssetAssignmentAnalyticsService(BaseAnalyticsService):
    def __init__(self, repo: AssetAssignmentAnalyticsRepository):
        self.repo = repo

    async def list_assignments(
        self,
        filters: AssetAssignmentFilterInput,
        pagination: PaginationParamsSchema,
        current_user: CurrentUserSchema,
    ) -> PageOutSchema[AssetAssignmentDetailOut]:
        assignments, total = await self.repo.list_assignments(filters, pagination)

        items = [
            AssetAssignmentDetailOut(
                id=UUID(str(a.id)),
                asset_id=a.asset_id,
                asset_name=a.asset.name if a.asset else "Unknown",
                user_id=a.user_id,
                user_name=a.user.full_name if a.user else "Unknown",
                user_email=self.filter_email(
                    a.user.email if a.user else "", current_user
                ),
                assigned_at=a.assigned_at,
                unassigned_at=a.unassigned_at,
                status="active" if a.unassigned_at is None else "inactive",
                duration_metrics=AssignmentDurationMetrics(
                    duration_days=self.calculate_duration_days(
                        a.assigned_at, a.unassigned_at
                    )
                    or Decimal("0"),
                    duration_formatted=self.format_duration(
                        a.assigned_at, a.unassigned_at
                    ),
                    is_active=a.unassigned_at is None,
                ),
            )
            for a in assignments
        ]

        return PageOutSchema(
            items=items, total=total, page=pagination.page, limit=pagination.limit
        )

    async def list_active_assignments(
        self,
        pagination: PaginationParamsSchema,
        current_user: CurrentUserSchema,
    ) -> PageOutSchema[AssetAssignmentDetailOut]:
        """List currently active assignments only."""
        filters = AssetAssignmentFilterInput(status="active")  # type: ignore
        return await self.list_assignments(filters, pagination, current_user)

    async def get_user_summary(
        self, user_id: UUID, current_user: CurrentUserSchema
    ) -> UserAssignmentSummary:
        summary = await self.repo.get_user_assignment_summary(user_id)
        summary["user_email"] = self.filter_email(summary["user_email"], current_user)
        return UserAssignmentSummary(**summary)

    async def get_asset_timeline(
        self, asset_id: UUID, current_user: CurrentUserSchema
    ) -> AssetAssignmentTimeline:
        assignments = await self.repo.get_assignment_timeline(asset_id)
        asset = assignments[0].asset if assignments else None

        timeline_entries = [
            AssignmentTimelineEntry(
                sequence=i + 1,
                assigned_at=a.assigned_at,
                unassigned_at=a.unassigned_at,
                user_id=a.user_id,
                user_name=a.user.full_name if a.user else "Unknown",
                duration_days=self.calculate_duration_days(
                    a.assigned_at, a.unassigned_at
                ),
            )
            for i, a in enumerate(assignments)
        ]

        active_assignment = None
        for a in assignments:
            if a.unassigned_at is None:
                active_assignment = AssetAssignmentOut(
                    id=UUID(str(a.id)),
                    asset_id=a.asset_id,
                    asset_name=asset.name if asset else "Unknown",
                    user_id=a.user_id,
                    user_name=a.user.full_name if a.user else "Unknown",
                    user_email=self.filter_email(
                        a.user.email if a.user else "", current_user
                    ),
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

    async def get_aggregates(
        self, filters: AssetAssignmentFilterInput
    ) -> AssignmentAggregates:
        agg_dict = await self.repo.get_aggregates(filters)

        most_assigned = await self.repo.get_most_assigned_asset()
        if most_assigned:
            agg_dict["most_frequently_assigned_asset_id"] = most_assigned[0]
            agg_dict["most_frequently_assigned_asset_name"] = most_assigned[1]

        most_active = await self.repo.get_most_active_user()
        if most_active:
            agg_dict["most_active_user_id"] = most_active[0]
            agg_dict["most_active_user_name"] = most_active[1]

        return AssignmentAggregates(**agg_dict)
