from repositories.analytics.cost_analytics_repo import CostAnalyticsRepository
from schemas.analytics.costs import AssetCostAnalyticsOut, RegionCostAnalyticsOut, RepairCostAnalyticsOut
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class CostAnalyticsService(BaseAnalyticsService):
    def __init__(self, repo: CostAnalyticsRepository):
        self.repo = repo

    async def get_repair_costs(self, pagination: PaginationParamsSchema) -> PageOutSchema[RepairCostAnalyticsOut]:
        rows, total = await self.repo.list_repair_costs(pagination)
        items = [
            RepairCostAnalyticsOut(
                repair_id=row.id,
                asset_id=row.asset_id,
                asset_name=row.asset_name,
                reported_at=row.created_at,
                labor_cost=self.safe_money(row.labor_cost),
                parts_cost=self.safe_money(row.parts_cost),
                total_cost=self.safe_money(row.total_cost),
            )
            for row in rows
        ]
        return PageOutSchema(items=items, total=total, page=pagination.page, limit=pagination.limit)

    async def get_asset_costs(self, pagination: PaginationParamsSchema) -> PageOutSchema[AssetCostAnalyticsOut]:
        rows, total = await self.repo.list_asset_costs(pagination)
        items = [
            AssetCostAnalyticsOut(
                asset_id=row.id,
                asset_name=row.name,
                asset_tag=row.asset_tag,
                purchase_cost=self.safe_money(row.purchase_cost),
                repair_cost=self.safe_money(row.repair_cost),
                total_cost=self.safe_money((row.purchase_cost or 0) + (row.repair_cost or 0)),
            )
            for row in rows
        ]
        return PageOutSchema(items=items, total=total, page=pagination.page, limit=pagination.limit)

    async def get_region_costs(self, pagination: PaginationParamsSchema) -> PageOutSchema[RegionCostAnalyticsOut]:
        rows, total = await self.repo.list_region_costs(pagination)
        items = [
            RegionCostAnalyticsOut(
                region_id=row.id,
                region_name=row.name,
                purchase_cost=self.safe_money(row.purchase_cost),
                repair_cost=self.safe_money(row.repair_cost),
                total_cost=self.safe_money((row.purchase_cost or 0) + (row.repair_cost or 0)),
            )
            for row in rows
        ]
        return PageOutSchema(items=items, total=total, page=pagination.page, limit=pagination.limit)
