from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset_maintenance import AssetMaintenance
from repositories.base import BaseRepository


class AssetMaintenanceRepository(BaseRepository):
    """Репозиторий для технического обслуживания активов"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> AssetMaintenance:
        """Create maintenance record"""
        maintenance = AssetMaintenance(**data)
        self.add(maintenance)
        await self.flush()
        await self.refresh(maintenance)
        return maintenance

    async def get(self, maintenance_id: UUID) -> AssetMaintenance | None:
        """Получить запись по ID"""
        result = await self.session.execute(
            select(AssetMaintenance).where(AssetMaintenance.id == maintenance_id)
        )
        return result.scalar_one_or_none()

    async def get_by_asset(self, asset_id: UUID) -> list[AssetMaintenance]:
        """Получить все записи обслуживания для актива"""
        result = await self.session.execute(
            select(AssetMaintenance)
            .where(AssetMaintenance.asset_id == asset_id)
            .order_by(AssetMaintenance.performed_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, maintenance_id: UUID, data: dict) -> AssetMaintenance | None:
        """Обновить запись обслуживания"""
        await self.session.execute(
            update(AssetMaintenance)
            .where(AssetMaintenance.id == maintenance_id)
            .values(**data)
        )
        await self.flush()
        return await self.get(maintenance_id)

    async def delete(self, maintenance_id: UUID) -> bool:
        """Удалить запись обслуживания"""
        result = await self.session.execute(
            delete(AssetMaintenance).where(AssetMaintenance.id == maintenance_id)
        )
        await self.flush()
        return self._rowcount(result) > 0

    async def delete_by_asset(self, asset_id: UUID) -> int:
        """Удалить все записи обслуживания актива"""
        result = await self.session.execute(
            delete(AssetMaintenance).where(AssetMaintenance.asset_id == asset_id)
        )
        await self.flush()
        return self._rowcount(result)
