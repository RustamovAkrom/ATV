from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.repairs.repair import Repair
from repositories.base import BaseRepository


class RepairAnalyticsRepository(BaseRepository):
    @staticmethod
    def _scope_filters(
        region_id: UUID | None,
        service_id: UUID | None,
        scoped_region_id: UUID | None,
        scoped_service_id: UUID | None,
    ):
        filters = []
        if scoped_region_id or region_id:
            filters.append(Asset.region_id == (scoped_region_id or region_id))
        if scoped_service_id or service_id:
            filters.append(Asset.service_id == (scoped_service_id or service_id))
        return filters

    @staticmethod
    def _date_filters(date_from: date | None, date_to: date | None):
        filters = []
        if date_from:
            filters.append(Repair.created_at >= datetime.combine(date_from, time.min))
        if date_to:
            filters.append(Repair.created_at <= datetime.combine(date_to, time.max))
        return filters

    async def metrics(
        self,
        region_id: UUID | None,
        service_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
        scoped_region_id: UUID | None,
        scoped_service_id: UUID | None,
    ):
        filters = self._scope_filters(
            region_id, service_id, scoped_region_id, scoped_service_id
        )
        dfilters = self._date_filters(date_from, date_to)
        per_asset = (
            await self.execute(
                select(
                    Asset.id.label("asset_id"),
                    Asset.name.label("asset_name"),
                    func.count(Repair.id).label("repair_count"),
                    func.coalesce(func.sum(Repair.labor_cost), 0).label("total_repair_cost"),
                )
                .select_from(Asset)
                .outerjoin(Repair, Repair.asset_id == Asset.id)
                .where(*filters, *dfilters)
                .group_by(Asset.id, Asset.name)
                .order_by(func.count(Repair.id).desc())
            )
        ).all()
        avg = (
            await self.execute(
                select(func.coalesce(func.avg(Repair.labor_cost), 0).label("avg_cost"))
                .select_from(Repair)
                .join(Asset, Asset.id == Repair.asset_id)
                .where(*filters, *dfilters)
            )
        ).one()
        return {"per_asset": per_asset, "average_repair_cost": float(avg.avg_cost or 0)}
