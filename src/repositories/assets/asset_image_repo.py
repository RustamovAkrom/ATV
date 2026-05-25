from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset_image import AssetImage
from repositories.base import BaseRepository


class AssetImageRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, image_data: dict) -> AssetImage:
        """Создать изображение актива"""
        image = AssetImage(**image_data)
        self.add(image)
        await self.flush()
        await self.refresh(image)
        return image

    async def get(self, image_id: UUID) -> AssetImage | None:
        """Получить изображение по ID"""
        result = await self.session.execute(
            select(AssetImage).where(AssetImage.id == image_id)
        )
        return result.scalar_one_or_none()

    async def get_by_asset(self, asset_id: UUID) -> list[AssetImage]:
        """Получить все изображения актива"""
        result = await self.session.execute(
            select(AssetImage)
            .where(AssetImage.asset_id == asset_id)
            .order_by(AssetImage.sort_order)
        )
        return result.scalars().all()

    async def get_primary(self, asset_id: UUID) -> AssetImage | None:
        """Получить главное изображение актива"""
        result = await self.session.execute(
            select(AssetImage)
            .where(AssetImage.asset_id == asset_id, AssetImage.is_primary == True)
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def set_primary(self, image_id: UUID, asset_id: UUID) -> None:
        """Установить изображение как главное (снимает флаг с других)"""
        # Снять флаг primary со всех изображений актива
        await self.session.execute(
            update(AssetImage)
            .where(AssetImage.asset_id == asset_id)
            .values(is_primary=False)
        )
        # Установить новый primary
        await self.session.execute(
            update(AssetImage).where(AssetImage.id == image_id).values(is_primary=True)
        )
        await self.flush()

    async def update_sort_order(self, image_id: UUID, sort_order: int) -> None:
        """Обновить порядок сортировки"""
        await self.session.execute(
            update(AssetImage)
            .where(AssetImage.id == image_id)
            .values(sort_order=sort_order)
        )
        await self.flush()

    async def delete(self, image_id: UUID) -> bool:
        """Удалить изображение"""
        result = await self.session.execute(
            delete(AssetImage).where(AssetImage.id == image_id)
        )
        await self.flush()
        return result.rowcount > 0

    async def delete_by_asset(self, asset_id: UUID) -> int:
        """Удалить все изображения актива"""
        result = await self.session.execute(
            delete(AssetImage).where(AssetImage.asset_id == asset_id)
        )
        await self.flush()
        return result.rowcount
