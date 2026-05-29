# services/analytics/asset_history_analytics_service.py

from schemas.analytics.asset_history import (
    AssetHistoryAggregates,
    AssetHistoryFilter,
    AssetHistoryOut,
    AssetHistoryPage,
)
from schemas.pagination import PageOutSchema, PaginationParamsSchema


class AssetHistoryAnalyticsService:
    """Service for asset history analytics."""

    def __init__(self, repo):
        self.repo = repo

    async def list(
        self,
        filters: AssetHistoryFilter,
        pagination: PaginationParamsSchema,
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

        return PageOutSchema(
            items=history_out,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get_aggregates(
        self, filters: AssetHistoryFilter
    ) -> AssetHistoryAggregates:
        agg_dict = await self.repo.get_aggregates(filters)

        return AssetHistoryAggregates(
            total_entries=agg_dict.get("total_entries", 0),
            unique_assets=agg_dict.get("unique_assets", 0),
            unique_users=agg_dict.get("unique_users", 0),
            date_range_start=agg_dict.get("date_range_start"),
            date_range_end=agg_dict.get("date_range_end"),
            actions_breakdown=agg_dict.get("actions_breakdown", []),
            most_active_asset_id=agg_dict.get("most_active_asset_id"),
            most_active_asset_name=agg_dict.get("most_active_asset_name"),
            most_active_user_id=agg_dict.get("most_active_user_id"),
            most_active_user_name=agg_dict.get("most_active_user_name"),
        )
