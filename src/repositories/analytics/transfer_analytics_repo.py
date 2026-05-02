from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from sqlalchemy import cast, Date, func, select

from db.models.assets.asset import Asset
from db.models.assets.asset_transfer import AssetTransfer
from repositories.base import BaseRepository


class TransferAnalyticsRepository(BaseRepository):
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
            filters.append(AssetTransfer.created_at >= datetime.combine(date_from, time.min))
        if date_to:
            filters.append(AssetTransfer.created_at <= datetime.combine(date_to, time.max))
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
        per_period = (
            await self.execute(
                select(
                    cast(AssetTransfer.created_at, Date).label("period"),
                    func.count(AssetTransfer.id).label("transfer_count"),
                )
                .join(Asset, Asset.id == AssetTransfer.asset_id)
                .where(*filters, *dfilters)
                .group_by(cast(AssetTransfer.created_at, Date))
                .order_by(cast(AssetTransfer.created_at, Date))
            )
        ).all()
        per_asset = (
            await self.execute(
                select(
                    Asset.id.label("asset_id"),
                    Asset.name.label("asset_name"),
                    func.count(AssetTransfer.id).label("transfer_count"),
                )
                .join(AssetTransfer, AssetTransfer.asset_id == Asset.id)
                .where(*filters, *dfilters)
                .group_by(Asset.id, Asset.name)
                .order_by(func.count(AssetTransfer.id).desc())
            )
        ).all()
        return {"per_period": per_period, "per_asset": per_asset}
