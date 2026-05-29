from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.org.region import Region
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class CostAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики затрат"""

    def _repair_parts_subquery(self):
        """Подзапрос для стоимости запчастей"""
        return (
            select(
                RepairPart.repair_id.label("repair_id"),
                func.sum(RepairPart.quantity * RepairPart.unit_price).label(
                    "parts_cost"
                ),
            )
            .group_by(RepairPart.repair_id)
            .subquery()
        )

    async def list_repair_costs(self, pagination):
        """Список затрат на ремонты"""
        repair_parts = self._repair_parts_subquery()

        query = (
            select(
                Repair.id,
                Repair.asset_id,
                Asset.name.label("asset_name"),
                Repair.created_at,
                func.coalesce(Repair.labor_cost, 0).label("labor_cost"),
                func.coalesce(repair_parts.c.parts_cost, 0).label("parts_cost"),
                (
                    func.coalesce(Repair.labor_cost, 0)
                    + func.coalesce(repair_parts.c.parts_cost, 0)
                ).label("total_cost"),
            )
            .join(Asset, Asset.id == Repair.asset_id)
            .outerjoin(repair_parts, repair_parts.c.repair_id == Repair.id)
            .order_by(
                (
                    func.coalesce(Repair.labor_cost, 0)
                    + func.coalesce(repair_parts.c.parts_cost, 0)
                ).desc(),
                Repair.created_at.desc(),
            )
        )

        result, total = await self.execute_with_pagination(query, pagination)
        return result.all(), total

    async def list_asset_costs(self, pagination):
        """Список затрат по активам"""
        repair_parts = self._repair_parts_subquery()

        query = (
            select(
                Asset.id,
                Asset.name,
                func.coalesce(Asset.purchase_cost, 0).label("purchase_cost"),
                func.coalesce(
                    func.sum(
                        func.coalesce(Repair.labor_cost, 0)
                        + func.coalesce(repair_parts.c.parts_cost, 0)
                    ),
                    0,
                ).label("repair_cost"),
            )
            .outerjoin(Repair, Repair.asset_id == Asset.id)
            .outerjoin(repair_parts, repair_parts.c.repair_id == Repair.id)
            .group_by(Asset.id, Asset.name, Asset.purchase_cost)
            .order_by(
                (
                    func.coalesce(Asset.purchase_cost, 0)
                    + func.coalesce(
                        func.sum(
                            func.coalesce(Repair.labor_cost, 0)
                            + func.coalesce(repair_parts.c.parts_cost, 0)
                        ),
                        0,
                    )
                ).desc()
            )
        )

        result, total = await self.execute_with_pagination(query, pagination)
        return result.all(), total

    async def list_region_costs(self, pagination):
        """Список затрат по регионам"""
        repair_parts = self._repair_parts_subquery()

        purchase_costs = (
            select(
                Asset.region_id.label("region_id"),
                func.sum(func.coalesce(Asset.purchase_cost, 0)).label("purchase_cost"),
            )
            .where(Asset.region_id.isnot(None))
            .group_by(Asset.region_id)
            .subquery()
        )

        repair_costs = (
            select(
                Asset.region_id.label("region_id"),
                func.sum(
                    func.coalesce(Repair.labor_cost, 0)
                    + func.coalesce(repair_parts.c.parts_cost, 0)
                ).label("repair_cost"),
            )
            .join(Repair, Repair.asset_id == Asset.id)
            .outerjoin(repair_parts, repair_parts.c.repair_id == Repair.id)
            .where(Asset.region_id.isnot(None))
            .group_by(Asset.region_id)
            .subquery()
        )

        query = (
            select(
                Region.id,
                Region.name,
                func.coalesce(purchase_costs.c.purchase_cost, 0).label("purchase_cost"),
                func.coalesce(repair_costs.c.repair_cost, 0).label("repair_cost"),
            )
            .outerjoin(purchase_costs, purchase_costs.c.region_id == Region.id)
            .outerjoin(repair_costs, repair_costs.c.region_id == Region.id)
            .order_by(
                (
                    func.coalesce(purchase_costs.c.purchase_cost, 0)
                    + func.coalesce(repair_costs.c.repair_cost, 0)
                ).desc()
            )
        )

        result, total = await self.execute_with_pagination(query, pagination)
        return result.all(), total
