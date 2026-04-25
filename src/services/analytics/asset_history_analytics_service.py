# services/analytics/asset_history_analytics_service.py

from schemas.analytics.asset_history import (
    AssetHistoryFilter,
    AssetHistoryOut,
    AssetHistoryPage,
    AssetHistoryAggregates,
)
from schemas.pagination import PaginationParams, PageOut, build_page


class AssetHistoryAnalyticsService:
    """Service for asset history analytics."""

    def __init__(self, repo):
        self.repo = repo

    async def list(
        self,
        filters: AssetHistoryFilter,
        pagination: PaginationParams,
    ) -> AssetHistoryPage:
        """List asset history with pagination."""
        items, total = await self.repo.list(filters, pagination)

        history_out = [
            AssetHistoryOut(
                id=i.id,
                asset_id=i.asset_id,
                asset_name=i.asset.name if i.asset else "Unknown",
                user_id=i.user_id,
                user_name=i.user.full_name if i.user else "Unknown",
                action=i.action,
                description=i.description,
                created_at=i.created_at,
            )
            for i in items
        ]

        return build_page(
            schema=PageOut[AssetHistoryOut],
            items=history_out,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get_aggregates(self, filters: AssetHistoryFilter) -> AssetHistoryAggregates:
        """Get aggregated history metrics."""
        agg_dict = await self.repo.get_aggregates(filters)

        # Build actions breakdown objects
        actions_breakdown = [
            {
                "action": a["action"],
                "count": a["count"],
                "last_occurrence": a["last_occurrence"],
                "first_occurrence": a["first_occurrence"],
            }
            for a in agg_dict["actions_breakdown"]
        ]

        return AssetHistoryAggregates(
            total_entries=agg_dict["total_entries"],
            unique_assets=agg_dict["unique_assets"],
            unique_users=agg_dict["unique_users"],
            date_range_start=agg_dict["date_range_start"],
            date_range_end=agg_dict["date_range_end"],
            actions_breakdown=actions_breakdown,
            most_active_asset_id=agg_dict["most_active_asset_id"],
            most_active_asset_name=agg_dict["most_active_asset_name"],
            most_active_user_id=agg_dict["most_active_user_id"],
            most_active_user_name=agg_dict["most_active_user_name"],
        )
