from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from api.dependencies.assets.asset_image import get_asset_image_service
from api.dependencies.storage import get_file_upload_service
from core.cache.decorators import cached, invalidate_cache
from core.config import get_settings
from core.security.auth.dependencies import get_current_user
from core.slowapi import limiter
from core.storage import FileUploadService
from core.storage.configs import UploadConfigs
from core.security.rbac.presets import ImagesPermissions
from schemas.assets.asset_image import AssetImageCreateSchema, AssetImageOutSchema
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from services.assets.asset_image_service import AssetImageService


router = APIRouter(prefix="/assets/{asset_id}/images", tags=["Asset Images"])
settings = get_settings()


# ========== GET запросы (без rate limit) ==========


@router.get(
    "/",
    response_model=list[AssetImageOutSchema],
    dependencies=[Depends(ImagesPermissions.CanViewImages)],
)
@cached(tags=("asset:image:list",))
async def list_asset_images(
    asset_id: UUID,
    service: AssetImageService = Depends(get_asset_image_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Список изображений актива"""
    return await service.get_images(asset_id, actor)


@router.get(
    "/file/{image_id}",
    dependencies=[Depends(ImagesPermissions.CanViewImages)]
)
@cached(tags=("asset:image:file",))
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


@router.post(
    "/",
    response_model=AssetImageOutSchema,
    dependencies=[Depends(ImagesPermissions.CanUploadImages)],
)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:detail",
        "asset:history",
        "asset:image:list",
        "asset:image:file",
    )
)
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


@router.put(
    "/{image_id}/primary",
    dependencies=[Depends(ImagesPermissions.CanUploadImages)],
)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:detail",
        "asset:history",
        "asset:image:list",
        "asset:image:file",
    )
)
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


@router.delete(
    "/{image_id}",
    response_model=StatusResponse,
    dependencies=[Depends(ImagesPermissions.CanDeleteImages)],
)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:detail",
        "asset:image:list",
        "asset:image:file",
    )
)
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
    return StatusResponse(status="deleted", message="Image deleted successfully")


@router.post(
    "/reorder",
    response_model=StatusResponse,
    dependencies=[Depends(ImagesPermissions.CanUpdateImages)],
)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:detail",
        "asset:image:list",
    )
)
async def reorder_images(
    request: Request,
    asset_id: UUID,
    ordered_ids: list[UUID],
    service: AssetImageService = Depends(get_asset_image_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Изменить порядок изображений"""
    await service.reorder_images(asset_id, ordered_ids, actor)
    return StatusResponse(status="ok", message="Order updated")
