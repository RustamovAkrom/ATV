from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import Date, cast, func, select

from db.models.assets.asset import Asset
from db.models.assets.asset_transfer import AssetTransfer
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class TransferAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики трансферов (упрощенная версия)"""

    async def metrics(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> dict:
        """Метрики по трансферам"""
        filters = self.scope_filters(
            Asset, region_id, service_id, scoped_region_id, scoped_service_id
        )
        date_filters = self.date_filters(AssetTransfer.created_at, date_from, date_to)

        # По периодам
        per_period_query = (
            select(
                cast(AssetTransfer.created_at, Date).label("period"),
                func.count(AssetTransfer.id).label("transfer_count"),
            )
            .join(Asset, Asset.id == AssetTransfer.asset_id)
            .where(*filters, *date_filters)
            .group_by(cast(AssetTransfer.created_at, Date))
            .order_by(cast(AssetTransfer.created_at, Date))
        )

        per_period = (await self.session.execute(per_period_query)).all()

        # По активам
        per_asset_query = (
            select(
                Asset.id.label("asset_id"),
                Asset.name.label("asset_name"),
                func.count(AssetTransfer.id).label("transfer_count"),
            )
            .join(AssetTransfer, AssetTransfer.asset_id == Asset.id)
            .where(*filters, *date_filters)
            .group_by(Asset.id, Asset.name)
            .order_by(func.count(AssetTransfer.id).desc())
        )

        per_asset = (await self.session.execute(per_asset_query)).all()

        return {
            "per_period": per_period,
            "per_asset": per_asset,
        }
