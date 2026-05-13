from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_history import AssetHistory
from db.models.warehouse.warehouse import Warehouse
from repositories.base import BaseRepository


class WarehouseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        return await self.scalar(
            select(Asset)
            .options(selectinload(Asset.warehouse))
            .where(Asset.id == asset_id)
        )

    async def get_warehouse(self, warehouse_id: UUID) -> Warehouse | None:
        return await self.session.get(Warehouse, warehouse_id)

