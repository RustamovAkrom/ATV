from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload, selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_history import AssetHistory
from db.models.assets.asset_transfer import AssetTransfer
from db.models.org.service import Service
from db.models.warehouse.warehouse import Warehouse


class AssetTransferRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        result = await self.session.execute(
            select(Asset)
            .options(selectinload(Asset.transfers), selectinload(Asset.warehouse))
            .where(Asset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def get_asset_for_update(self, asset_id: UUID) -> Asset | None:
        result = await self.session.execute(
            select(Asset)
            .options(lazyload("*"))
            .where(Asset.id == asset_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_transfer(self, transfer_id: UUID) -> AssetTransfer | None:
        result = await self.session.execute(
            select(AssetTransfer).where(AssetTransfer.id == transfer_id)
        )
        return result.scalar_one_or_none()

    async def get_transfer_for_update(self, transfer_id: UUID) -> AssetTransfer | None:
        result = await self.session.execute(
            select(AssetTransfer)
            .where(AssetTransfer.id == transfer_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_warehouse(self, warehouse_id: UUID) -> Warehouse | None:
        return await self.session.get(Warehouse, warehouse_id)

    async def get_service(self, service_id: UUID) -> Service | None:
        return await self.session.get(Service, service_id)

    async def create_transfer(self, transfer: AssetTransfer) -> AssetTransfer:
        self.session.add(transfer)
        await self.session.flush()
        return transfer

    async def add_history(
        self, asset_id: UUID, user_id: UUID, action: str, description: str
    ) -> AssetHistory:
        entry = AssetHistory(
            asset_id=asset_id,
            user_id=user_id,
            action=action,
            description=description,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def flush(self) -> None:
        await self.session.flush()
