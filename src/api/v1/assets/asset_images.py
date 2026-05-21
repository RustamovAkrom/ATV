from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse

from api.dependencies.assets.asset_image import get_asset_image_service
from api.dependencies.storage import get_file_upload_service
from core.cache.decorators import invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from core.slowapi import limiter
from core.config import get_settings
from core.storage import FileUploadService
from core.storage.configs import UploadConfigs

from schemas.auth import CurrentUserSchema
from schemas.assets.asset_image import AssetImageOutSchema, AssetImageCreateSchema
from services.assets.asset_image_service import AssetImageService

router = APIRouter(prefix="/assets/{asset_id}/images", tags=["Asset Images"])
settings = get_settings()


# ========== GET запросы (без rate limit) ==========

@router.get("/", response_model=list[AssetImageOutSchema])
async def list_asset_images(
    asset_id: UUID,
    service: AssetImageService = Depends(get_asset_image_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Список изображений актива"""
    return await service.get_images(asset_id, actor)


@router.get("/file/{image_id}")
async def get_image_file(
    image_id: UUID,
    service: AssetImageService = Depends(get_asset_image_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    """Получить файл изображения"""
    image = await service.repo.get(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Проверяем доступ к активу
    await service._check_asset_access(image.asset_id, current_user)

    full_path = settings.BASE_DIR / image.file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=full_path,
        filename=image.file_name,
        media_type=image.content_type,
    )


# ========== POST/PATCH/DELETE запросы (с rate limit) ==========

@router.post("/", response_model=AssetImageOutSchema)
@limiter.limit("20/minute")
@invalidate_cache(tags=("assets:list", "assets:detail"))
async def upload_asset_image(
    request: Request,
    asset_id: UUID,
    file: UploadFile = File(...),
    service: AssetImageService = Depends(get_asset_image_service),
    actor: CurrentUserSchema = Depends(get_current_user),
    upload_service: FileUploadService = Depends(get_file_upload_service),
):
    """Загрузить изображение для актива"""
    try:
        result = await upload_service.upload(
            file=file,
            folder=settings.STORAGE_ASSET_IMAGE_FOLDER,
            validator=UploadConfigs.asset_image(),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Получаем размеры изображения (если PIL установлен)
    width, height = None, None
    try:
        from PIL import Image
        full_path = settings.BASE_DIR / result.file_path
        with Image.open(full_path) as img:
            width, height = img.size
    except ImportError:
        pass

    create_data = AssetImageCreateSchema(
        file_name=result.original_name,
        file_path=result.file_path,
        file_size=result.file_size,
        content_type=file.content_type,
        width=width,
        height=height,
    )

    return await service.upload_image(asset_id, create_data, actor)


@router.put("/{image_id}/primary")
@limiter.limit("10/minute")
@invalidate_cache(tags=("assets:list", "assets:detail"))
async def set_primary_image(
    request: Request,
    asset_id: UUID,
    image_id: UUID,
    service: AssetImageService = Depends(get_asset_image_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Установить главное изображение"""
    await service.set_primary(image_id, asset_id, actor)
    return {"status": "ok", "message": "Primary image set"}


@router.delete("/{image_id}")
@limiter.limit("10/minute")
@invalidate_cache(tags=("assets:list", "assets:detail"))
async def delete_asset_image(
    request: Request,
    asset_id: UUID,
    image_id: UUID,
    service: AssetImageService = Depends(get_asset_image_service),
    actor: CurrentUserSchema = Depends(get_current_user),
    upload_service: FileUploadService = Depends(get_file_upload_service),
):
    """Удалить изображение"""
    # Получаем информацию об изображении
    image = await service.repo.get(image_id)
    if not image or image.asset_id != asset_id:
        raise HTTPException(status_code=404, detail="Image not found")

    # Удаляем физический файл
    try:
        await upload_service.delete(image.file_path)
    except Exception:
        pass  # Логируем, но не прерываем удаление записи

    # Удаляем запись из БД
    await service.delete_image(image_id, asset_id, actor)
    return {"status": "deleted", "message": "Image deleted successfully"}


@router.post("/reorder")
@limiter.limit("10/minute")
@invalidate_cache(tags=("assets:list", "assets:detail"))
async def reorder_images(
    request: Request,
    asset_id: UUID,
    ordered_ids: list[UUID],
    service: AssetImageService = Depends(get_asset_image_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Изменить порядок изображений"""
    await service.reorder_images(asset_id, ordered_ids, actor)
    return {"status": "ok", "message": "Order updated"}
