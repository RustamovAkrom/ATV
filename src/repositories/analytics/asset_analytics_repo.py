from __future__ import annotations

from uuid import UUID

from sqlalchemy import case, cast, Float, func, select

from db.models.assets.asset import Asset
from db.models.enums import LifecycleStage
from db.models.org.region import Region
from db.models.org.service import Service
from db.models.warehouse.warehouse import Warehouse
from repositories.base import BaseRepository


class AssetAnalyticsRepository(BaseRepository):
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

    async def distribution(
        self,
        region_id: UUID | None,
        service_id: UUID | None,
        scoped_region_id: UUID | None,
        scoped_service_id: UUID | None,
    ) -> dict:
        filters = self._scope_filters(
            region_id, service_id, scoped_region_id, scoped_service_id
        )
        total_assets = int(
            (await self.execute(select(func.count(Asset.id)).where(*filters))).scalar_one()
            or 0
        )
        by_region = (
            await self.execute(
                select(Region.id, Region.name, func.count(Asset.id).label("asset_count"))
                .select_from(Region)
                .outerjoin(Asset, Asset.region_id == Region.id)
                .where(*filters)
                .group_by(Region.id, Region.name)
            )
        ).all()
        by_service = (
            await self.execute(
                select(Service.id, Service.name, func.count(Asset.id).label("asset_count"))
                .select_from(Service)
                .outerjoin(Asset, Asset.service_id == Service.id)
                .where(*filters)
                .group_by(Service.id, Service.name)
            )
        ).all()
        by_warehouse = (
            await self.execute(
                select(
                    Warehouse.id,
                    Warehouse.name,
                    func.count(Asset.id).label("asset_count"),
                )
                .select_from(Warehouse)
                .outerjoin(Asset, Asset.current_warehouse_id == Warehouse.id)
                .where(*filters)
                .group_by(Warehouse.id, Warehouse.name)
            )
        ).all()
        by_status = (
            await self.execute(
                select(Asset.status, func.count(Asset.id).label("asset_count"))
                .where(*filters)
                .group_by(Asset.status)
            )
        ).all()
        geo = (
            await self.execute(
                select(
                    Region.id.label("region_id"),
                    Region.name.label("region_name"),
                    func.count(Asset.id).label("asset_count"),
                    func.count(Asset.id)
                    .filter(Asset.condition_percent <= 35)
                    .label("critical_assets_count"),
                )
                .select_from(Region)
                .outerjoin(Asset, Asset.region_id == Region.id)
                .where(*filters)
                .group_by(Region.id, Region.name)
            )
        ).all()
        return {
            "total_assets": total_assets,
            "by_region": by_region,
            "by_service": by_service,
            "by_warehouse": by_warehouse,
            "by_status": by_status,
            "geo": geo,
        }

    async def lifecycle(
        self,
        region_id: UUID | None,
        service_id: UUID | None,
        scoped_region_id: UUID | None,
        scoped_service_id: UUID | None,
    ) -> dict:
        filters = self._scope_filters(
            region_id, service_id, scoped_region_id, scoped_service_id
        )
        ref_date = func.coalesce(Asset.commission_date, Asset.purchase_date)
        age_years = cast(func.extract("year", func.age(func.current_date(), ref_date)), Float)
        stage = case(
            (age_years < 2, LifecycleStage.NEW.value),
            (age_years < 5, LifecycleStage.NORMAL.value),
            (age_years < 10, LifecycleStage.OLD.value),
            else_=LifecycleStage.CRITICAL.value,
        )
        rows = (
            await self.execute(
                select(stage.label("stage"), func.count(Asset.id).label("asset_count"))
                .where(ref_date.isnot(None), *filters)
                .group_by(stage)
            )
        ).all()
        total = sum(int(r.asset_count or 0) for r in rows)
        critical = sum(
            int(r.asset_count or 0)
            for r in rows
            if str(r.stage) == LifecycleStage.CRITICAL.value
        )
        return {"rows": rows, "total": total, "critical": critical}
