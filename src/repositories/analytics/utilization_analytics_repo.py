from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.org.region import Region
from db.models.org.service import Service
from db.models.users.user import User
from repositories.base import BaseRepository


class UtilizationAnalyticsRepository(BaseRepository):
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

    async def metrics(
        self,
        region_id: UUID | None,
        service_id: UUID | None,
        scoped_region_id: UUID | None,
        scoped_service_id: UUID | None,
    ):
        filters = self._scope_filters(
            region_id, service_id, scoped_region_id, scoped_service_id
        )
        per_employee = (
            await self.execute(
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
        ).all()
        per_service = (
            await self.execute(
                select(
                    Service.id.label("service_id"),
                    Service.name.label("service_name"),
                    func.count(Asset.id).label("asset_count"),
                )
                .outerjoin(Asset, Asset.service_id == Service.id)
                .where(*filters)
                .group_by(Service.id, Service.name)
            )
        ).all()
        region_load = (
            await self.execute(
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
        ).all()
        return {
            "assets_per_employee": per_employee,
            "assets_per_service": per_service,
            "region_load": region_load,
        }
