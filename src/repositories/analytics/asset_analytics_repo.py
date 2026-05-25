from __future__ import annotations

from uuid import UUID

from sqlalchemy import Float, case, cast, func, select

from db.models.assets.asset import Asset
from db.models.enums import LifecycleStage
from db.models.org.region import Region
from db.models.org.service import Service
from db.models.warehouse.warehouse import Warehouse
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class AssetAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики активов"""

    async def distribution(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> dict:
        """Распределение активов по регионам, сервисам, складам и статусам"""
        filters = self.scope_filters(
            Asset, region_id, service_id, scoped_region_id, scoped_service_id
        )

        # Общее количество
        total_assets = await self.get_count(Asset, filters)

        # По регионам
        by_region_query = (
            select(Region.id, Region.name, func.count(Asset.id).label("asset_count"))
            .select_from(Region)
            .outerjoin(Asset, Asset.region_id == Region.id)
            .where(*filters)
            .group_by(Region.id, Region.name)
        )
        by_region = (await self.session.execute(by_region_query)).all()

        # По сервисам
        by_service_query = (
            select(Service.id, Service.name, func.count(Asset.id).label("asset_count"))
            .select_from(Service)
            .outerjoin(Asset, Asset.service_id == Service.id)
            .where(*filters)
            .group_by(Service.id, Service.name)
        )
        by_service = (await self.session.execute(by_service_query)).all()

        # По складам
        by_warehouse_query = (
            select(
                Warehouse.id, Warehouse.name, func.count(Asset.id).label("asset_count")
            )
            .select_from(Warehouse)
            .outerjoin(Asset, Asset.current_warehouse_id == Warehouse.id)
            .where(*filters)
            .group_by(Warehouse.id, Warehouse.name)
        )
        by_warehouse = (await self.session.execute(by_warehouse_query)).all()

        # По статусам
        by_status_query = (
            select(Asset.status, func.count(Asset.id).label("asset_count"))
            .where(*filters)
            .group_by(Asset.status)
        )
        by_status = (await self.session.execute(by_status_query)).all()

        # Гео-данные
        geo_query = (
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
        geo = (await self.session.execute(geo_query)).all()

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
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> dict:
        """Анализ жизненного цикла активов"""
        filters = self.scope_filters(
            Asset, region_id, service_id, scoped_region_id, scoped_service_id
        )

        ref_date = func.coalesce(Asset.commission_date, Asset.purchase_date)
        age_years = cast(
            func.extract("year", func.age(func.current_date(), ref_date)), Float
        )

        stage = case(
            (age_years < 2, LifecycleStage.NEW.value),
            (age_years < 5, LifecycleStage.NORMAL.value),
            (age_years < 10, LifecycleStage.OLD.value),
            else_=LifecycleStage.CRITICAL.value,
        )

        query = (
            select(stage.label("stage"), func.count(Asset.id).label("asset_count"))
            .where(ref_date.isnot(None), *filters)
            .group_by(stage)
        )

        rows = (await self.session.execute(query)).all()
        total = sum(int(r.asset_count or 0) for r in rows)
        critical = sum(
            int(r.asset_count or 0)
            for r in rows
            if str(r.stage) == LifecycleStage.CRITICAL.value
        )

        return {"rows": rows, "total": total, "critical": critical}
