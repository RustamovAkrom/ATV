from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from api.dependencies.documents.document import get_document_service
from api.dependencies.storage import get_file_upload_service
from core.cache.decorators import cached, invalidate_cache
from core.config import get_settings
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from core.slowapi import limiter
from core.storage import FileUploadService
from core.storage.configs import UploadConfigs
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from schemas.documents.document import (
    AssetDocumentCreateSchema,
    AssetDocumentOutSchema,
    AssetDocumentUpdateSchema,
    AssetDocumentWithFilesOutSchema,
)
from services.documents.document_service import DocumentService

settings = get_settings()
router = APIRouter(prefix="/assets/{asset_id}/documents", tags=["Asset Documents"])


# ========== GET запросы (без rate limit) ==========


@router.get("/", response_model=list[AssetDocumentOutSchema])
@cached(tags=("document:list",))
async def list_documents(
    asset_id: UUID,
    service: DocumentService = Depends(get_document_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Список всех документов актива"""
    return await service.list_by_asset(asset_id, actor)


@router.get("/{document_id}", response_model=AssetDocumentWithFilesOutSchema)
@cached(tags=("document:detail",))
async def get_document(
    asset_id: UUID,
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Получить информацию о документе"""
    return await service.get_document(asset_id, document_id, actor)


@router.get("/{document_id}/files/{file_id}")
@cached(tags=("document:download",))
async def download_file(
    asset_id: UUID,
    document_id: UUID,
    file_id: UUID,
    service: DocumentService = Depends(get_document_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Скачать файл документа"""
    # Проверяем существование документа
    document = await service.get_document(asset_id, document_id, actor)

    # Находим файл
    file_info = None
    for f in document.files:
        if f.id == file_id:
            file_info = f
            break

    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")

    # Полный путь к файлу
    full_path = settings.BASE_DIR / file_info.file_path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")

    return FileResponse(
        path=full_path,
        filename=file_info.file_name,
        media_type=file_info.content_type or "application/octet-stream",
    )


# ========== POST/PATCH/DELETE запросы (с rate limit) ==========


@router.post(
    "/",
    response_model=AssetDocumentOutSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "document:list",
        "document:detail",
        "document:download",
    )
)
async def attach_asset_document(
    request: Request,
    asset_id: UUID,
    title: str = Form(..., min_length=1, max_length=255),
    description: str | None = Form(None, max_length=500),
    document_type: str = Form("other", min_length=1, max_length=50),
    status: str = Form("draft"),
    files: list[UploadFile] = File(default=[]),
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    upload_service: FileUploadService = Depends(get_file_upload_service),
):
    """
    Создать документ с загрузкой файлов.
    Поддерживает multipart/form-data с файлами.
    """
    # Проверяем допустимые статусы
    from db.models.enums import DocumentStatus

    try:
        doc_status = DocumentStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    # Создаем документ
    create_data = AssetDocumentCreateSchema(
        title=title,
        description=description,
        document_type=document_type,
        status=doc_status,
    )

    document = await service.create_document(asset_id, create_data, actor)

    # Сохраняем файлы через единую систему загрузки
    uploaded_files = []
    for upload_file in files:
        try:
            result = await upload_service.upload(
                file=upload_file,
                folder=settings.STORAGE_DOCUMENT_FOLDER,
                validator=UploadConfigs.document(),
            )
            uploaded_files.append(
                {
                    "file_name": result.original_name,
                    "file_path": result.file_path,
                    "file_size": result.file_size,
                    "content_type": upload_file.content_type,
                }
            )
        except HTTPException as e:
            # Если файл не прошёл валидацию, удаляем созданный документ
            await service.delete_document(asset_id, document.id, actor)
            raise e

    # Добавляем файлы к документу
    for file_data in uploaded_files:
        await service.add_file_to_document(asset_id, document.id, file_data, actor)

    return await service.get_document(asset_id, document.id, actor)


@router.patch(
    "/{document_id}",
    response_model=AssetDocumentOutSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("30/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "document:list",
        "document:detail",
        "document:download",
    )
)
async def update_asset_document(
    request: Request,
    asset_id: UUID,
    document_id: UUID,
    data: AssetDocumentUpdateSchema,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Обновить информацию о документе"""
    return await service.update_document(asset_id, document_id, data, actor)


@router.post(
    "/{document_id}/files",
    response_model=dict,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "document:list",
        "document:detail",
        "document:download",
    )
)
async def add_file_to_document(
    request: Request,
    asset_id: UUID,
    document_id: UUID,
    file: UploadFile = File(...),
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    upload_service: FileUploadService = Depends(get_file_upload_service),
):
    """Добавить файл к существующему документу"""
    try:
        result = await upload_service.upload(
            file=file,
            folder=settings.STORAGE_DOCUMENT_FOLDER,
            validator=UploadConfigs.document(),
        )
    except HTTPException as e:
        raise e

    file_data = {
        "file_name": result.original_name,
        "file_path": result.file_path,
        "file_size": result.file_size,
        "content_type": file.content_type,
    }

    file_obj = await service.add_file_to_document(
        asset_id, document_id, file_data, actor
    )
    return {"message": "File added successfully", "file": file_obj.model_dump()}


@router.delete(
    "/{document_id}/files/{file_id}",
    response_model=StatusResponse,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "document:list",
        "document:detail",
        "document:download",
    )
)
async def delete_file_from_document(
    request: Request,
    asset_id: UUID,
    document_id: UUID,
    file_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    upload_service: FileUploadService = Depends(get_file_upload_service),
):
    """Удалить файл из документа"""
    # Получаем информацию о файле перед удалением
    document = await service.get_document(asset_id, document_id, actor)
    file_to_delete = None
    for f in document.files:
        if f.id == file_id:
            file_to_delete = f
            break

    if file_to_delete:
        # Удаляем физический файл
        await upload_service.delete(file_to_delete.file_path)

    # Удаляем запись из БД
    await service.delete_file_from_document(asset_id, document_id, file_id, actor)
    return StatusResponse(status="deleted", message="File deleted successfully")


@router.delete(
    "/{document_id}",
    response_model=StatusResponse,
    dependencies=[Depends(AssetPermissions.CanDeleteAssets)],
)
@limiter.limit("5/minute")
@invalidate_cache(
    tags=(
        "assets:list",
        "document:list",
        "document:detail",
        "document:download",
    )
)
async def delete_asset_document(
    request: Request,
    asset_id: UUID,
    document_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
    upload_service: FileUploadService = Depends(get_file_upload_service),
):
    """Удалить документ (каскадно удаляет все файлы)"""
    # Получаем документ с файлами
    document = await service.get_document(asset_id, document_id, actor)

    # Удаляем физические файлы
    for file in document.files:
        try:
            await upload_service.delete(file.file_path)
        except Exception:
            pass  # Логируем, но не прерываем удаление документа

    # Удаляем документ из БД
    await service.delete_document(asset_id, document_id, actor)
    return StatusResponse(
        status="deleted", message="Asset document successfully deleted"
    )
