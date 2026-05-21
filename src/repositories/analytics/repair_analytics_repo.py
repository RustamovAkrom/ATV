from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.repairs.repair import Repair
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class RepairAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики ремонтов"""

    async def metrics(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> dict:
        """Метрики по ремонтам"""
        filters = self.scope_filters(
            Asset, region_id, service_id, scoped_region_id, scoped_service_id
        )
        date_filters = self.date_filters(Repair.created_at, date_from, date_to)

        # По активам
        per_asset_query = select(
            Asset.id.label("asset_id"),
            Asset.name.label("asset_name"),
            func.count(Repair.id).label("repair_count"),
            func.coalesce(func.sum(Repair.labor_cost), 0).label("total_repair_cost"),
        ).select_from(Asset).outerjoin(Repair, Repair.asset_id == Asset.id).where(
            *filters, *date_filters
        ).group_by(Asset.id, Asset.name).order_by(func.count(Repair.id).desc())

        per_asset = (await self.session.execute(per_asset_query)).all()

        # Средняя стоимость
        avg_query = select(
            func.coalesce(func.avg(Repair.labor_cost), 0).label("avg_cost")
        ).select_from(Repair).join(Asset, Asset.id == Repair.asset_id).where(
            *filters, *date_filters
        )

        avg_result = (await self.session.execute(avg_query)).one()

        return {
            "per_asset": per_asset,
            "average_repair_cost": float(avg_result.avg_cost or 0),
        }
