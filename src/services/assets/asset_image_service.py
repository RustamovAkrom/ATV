from uuid import UUID

from core.exceptions.errors import NotFound
from core.security.access_control import AccessControl
from db.models.assets.asset_image import AssetImage
from repositories.assets.asset_image_repo import AssetImageRepository
from repositories.assets.asset_repo import AssetRepository
from schemas.assets.asset_image import (
    AssetImageCreateSchema,
    AssetImageOutSchema,
)
from schemas.auth.auth import CurrentUserSchema


class AssetImageService:
    def __init__(
        self,
        repo: AssetImageRepository,
        asset_repo: AssetRepository,
    ):
        self.repo = repo
        self.asset_repo = asset_repo

    async def _check_asset_access(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Проверить доступ к активу"""
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise NotFound(f"Asset {asset_id} not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

    async def upload_image(
        self,
        asset_id: UUID,
        data: AssetImageCreateSchema,
        actor: CurrentUserSchema,
    ) -> AssetImageOutSchema:
        """Загрузить изображение для актива"""
        await self._check_asset_access(asset_id, actor)

        # Проверяем, есть ли уже изображения (если нет — это будет primary)
        existing = await self.repo.get_by_asset(asset_id)
        is_primary = len(existing) == 0

        image = await self.repo.create(
            {
                "asset_id": asset_id,
                "file_name": data.file_name,
                "file_path": data.file_path,
                "file_size": data.file_size,
                "content_type": data.content_type,
                "is_primary": is_primary,
                "sort_order": len(existing),
                "width": data.width,
                "height": data.height,
                "alt_text": data.alt_text,
            }
        )

        return self._to_out(image)

    async def get_images(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> list[AssetImageOutSchema]:
        """Получить все изображения актива"""
        await self._check_asset_access(asset_id, actor)
        images = await self.repo.get_by_asset(asset_id)
        return [self._to_out(img) for img in images]

    async def set_primary(
        self, image_id: UUID, asset_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Установить главное изображение"""
        await self._check_asset_access(asset_id, actor)
        image = await self.repo.get(image_id)
        if not image or image.asset_id != asset_id:
            raise NotFound(f"Image {image_id} not found for asset {asset_id}")
        await self.repo.set_primary(image_id, asset_id)

    async def delete_image(
        self, image_id: UUID, asset_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Удалить изображение"""
        await self._check_asset_access(asset_id, actor)
        image = await self.repo.get(image_id)
        if not image or image.asset_id != asset_id:
            raise NotFound(f"Image {image_id} not found")
        await self.repo.delete(image_id)

        # Если удалили primary — назначаем первым в списке
        if image.is_primary:
            remaining = await self.repo.get_by_asset(asset_id)
            if remaining:
                await self.repo.set_primary(remaining[0].id, asset_id)

    async def reorder_images(
        self, asset_id: UUID, ordered_ids: list[UUID], actor: CurrentUserSchema
    ) -> None:
        """Изменить порядок изображений"""
        await self._check_asset_access(asset_id, actor)
        images = await self.repo.get_by_asset(asset_id)
        image_map = {img.id: img for img in images}

        for idx, img_id in enumerate(ordered_ids):
            if img_id in image_map:
                await self.repo.update_sort_order(img_id, idx)

    def _to_out(self, image: AssetImage) -> AssetImageOutSchema:
        return AssetImageOutSchema(
            id=image.id,
            asset_id=image.asset_id,
            file_name=image.file_name,
            file_path=image.file_path,
            file_size=image.file_size,
            content_type=image.content_type,
            is_primary=image.is_primary,
            sort_order=image.sort_order,
            width=image.width,
            height=image.height,
            alt_text=image.alt_text,
            created_at=image.created_at,
            updated_at=image.updated_at,
        )
