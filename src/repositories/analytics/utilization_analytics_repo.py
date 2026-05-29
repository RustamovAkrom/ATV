from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.org.region import Region
from db.models.org.service import Service
from db.models.users.user import User
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class UtilizationAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики утилизации"""

    async def metrics(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> dict:
        """Метрики утилизации ресурсов"""
        filters = self.scope_filters(
            Asset, region_id, service_id, scoped_region_id, scoped_service_id
        )

        # Активы на сотрудника
        per_employee_query = (
            select(
                User.id.label("user_id"),
                User.full_name.label("user_name"),
                func.count(AssetAssignment.asset_id).label("asset_count"),
            )
            .join(AssetAssignment, AssetAssignment.user_id == User.id)
            .join(Asset, Asset.id == AssetAssignment.asset_id)
            .where(AssetAssignment.unassigned_at.is_(None), *filters)
            .group_by(User.id, User.full_name)
            .order_by(func.count(AssetAssignment.asset_id).desc())
        )

        per_employee = (await self.session.execute(per_employee_query)).all()

        # Активы на сервис
        per_service_query = (
            select(
                Service.id.label("service_id"),
                Service.name.label("service_name"),
                func.count(Asset.id).label("asset_count"),
            )
            .outerjoin(Asset, Asset.service_id == Service.id)
            .where(*filters)
            .group_by(Service.id, Service.name)
        )

        per_service = (await self.session.execute(per_service_query)).all()

        # Загрузка регионов
        region_load_query = (
            select(
                Region.id.label("region_id"),
                Region.name.label("region_name"),
                func.count(Asset.id).label("asset_count"),
                func.count(func.distinct(Asset.owner_id)).label("employee_count"),
            )
            .outerjoin(Asset, Asset.region_id == Region.id)
            .where(*filters)
            .group_by(Region.id, Region.name)
        )

        region_load = (await self.session.execute(region_load_query)).all()

        # Расчет нагрузки регионов
        region_load_list = []
        for row in region_load:
            asset_count = row.asset_count or 0
            employee_count = row.employee_count or 0
            load_ratio = asset_count / employee_count if employee_count > 0 else 0

            region_load_list.append(
                {
                    "region_id": row.region_id,
                    "region_name": row.region_name,
                    "asset_count": asset_count,
                    "employee_count": employee_count,
                    "load_ratio": load_ratio,
                }
            )

        # Перегруженные и недогруженные регионы
        avg_load = (
            sum(r["load_ratio"] for r in region_load_list) / len(region_load_list)
            if region_load_list
            else 0
        )
        overloaded = [r for r in region_load_list if r["load_ratio"] > avg_load * 1.2]
        underutilized = [
            r for r in region_load_list if r["load_ratio"] < avg_load * 0.5
        ]

        return {
            "assets_per_employee": per_employee,
            "assets_per_service": per_service,
            "region_load": region_load_list,
            "overloaded_regions": overloaded,
            "underutilized_regions": underutilized,
        }
