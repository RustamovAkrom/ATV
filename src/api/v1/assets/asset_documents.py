import os
import uuid
import shutil
from pathlib import Path
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse

from api.dependencies.documents.document import get_document_service
from core.cache.decorators import invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from core.slowapi import limiter
from core.config import get_settings

from schemas.auth import CurrentUserSchema
from schemas.documents.document import (
    AssetDocumentCreateSchema,
    AssetDocumentUpdateSchema,
    AssetDocumentOutSchema,
    AssetDocumentWithFilesOutSchema,
)
from schemas.common import StatusResponse

from services.documents.document_service import DocumentService

settings = get_settings()
router = APIRouter(prefix="/assets/{asset_id}/documents", tags=["Asset Documents"])

# Директория для хранения файлов документов
DOCUMENTS_DIR = settings.BASE_DIR / "storage" / "documents"


def ensure_documents_dir():
    """Создать директорию для документов если её нет"""
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(upload_file: UploadFile, document_id: UUID) -> tuple[str, str, int]:
    """Сохранить загруженный файл и вернуть путь, имя, размер"""
    ensure_documents_dir()

    # Генерируем уникальное имя файла
    file_extension = os.path.splitext(upload_file.filename or "file")[1].lower()
    unique_filename = f"{document_id}_{uuid.uuid4().hex[:8]}{file_extension}"
    file_path = DOCUMENTS_DIR / unique_filename

    # Сохраняем файл
    content = upload_file.file.read()
    file_size = len(content)

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Возвращаем относительный путь для хранения в БД
    relative_path = f"storage/documents/{unique_filename}"

    return relative_path, upload_file.filename or "unknown", file_size


# ========== GET запросы (без rate limit) ==========

@router.get("/", response_model=list[AssetDocumentOutSchema])
async def list_documents(
    asset_id: UUID,
    service: DocumentService = Depends(get_document_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Список всех документов актива"""
    return await service.list_by_asset(asset_id, actor)


@router.get("/{document_id}", response_model=AssetDocumentWithFilesOutSchema)
async def get_document(
    asset_id: UUID,
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    """Получить информацию о документе"""
    return await service.get_document(asset_id, document_id, actor)


@router.get("/{document_id}/files/{file_id}")
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
@invalidate_cache(tags=("assets:list",))
async def attach_asset_document(
    request: Request,
    asset_id: UUID,
    title: str = Form(..., min_length=1, max_length=255),
    description: str | None = Form(None, max_length=500),
    document_type: str = Form("other", min_length=1, max_length=50),
    status: str = Form("draft"),
    files: List[UploadFile] = File(default=[]),
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
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

    # Сначала создаем документ без файлов
    create_data = AssetDocumentCreateSchema(
        title=title,
        description=description,
        document_type=document_type,
        status=doc_status,
    )

    document = await service.create_document(asset_id, create_data, actor)

    # Затем сохраняем файлы
    uploaded_files = []
    for upload_file in files:
        if upload_file.size and upload_file.size > settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File too large: {upload_file.filename}")

        file_path, file_name, file_size = save_upload_file(upload_file, document.id)
        uploaded_files.append({
            "file_name": file_name,
            "file_path": file_path,
            "file_size": file_size,
            "content_type": upload_file.content_type,
        })

    # Если есть файлы, добавляем их к документу
    for file_data in uploaded_files:
        await service.add_file_to_document(asset_id, document.id, file_data, actor)

    # Возвращаем обновленный документ
    return await service.get_document(asset_id, document.id, actor)


@router.patch(
    "/{document_id}",
    response_model=AssetDocumentOutSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("30/minute")
@invalidate_cache(tags=("assets:list",))
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
@invalidate_cache(tags=("assets:list",))
async def add_file_to_document(
    request: Request,
    asset_id: UUID,
    document_id: UUID,
    file: UploadFile = File(...),
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Добавить файл к существующему документу"""
    if file.size and file.size > settings.UPLOAD_MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large: {file.filename}")

    file_path, file_name, file_size = save_upload_file(file, document_id)
    file_data = {
        "file_name": file_name,
        "file_path": file_path,
        "file_size": file_size,
        "content_type": file.content_type,
    }

    result = await service.add_file_to_document(asset_id, document_id, file_data, actor)
    return {"message": "File added successfully", "file": result.model_dump()}


@router.delete(
    "/{document_id}/files/{file_id}",
    response_model=StatusResponse,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("assets:list",))
async def delete_file_from_document(
    request: Request,
    asset_id: UUID,
    document_id: UUID,
    file_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Удалить файл из документа"""
    await service.delete_file_from_document(asset_id, document_id, file_id, actor)
    return StatusResponse(status="deleted", message="File deleted successfully")


@router.delete(
    "/{document_id}",
    response_model=StatusResponse,
    dependencies=[Depends(AssetPermissions.CanDeleteAssets)],
)
@limiter.limit("5/minute")
@invalidate_cache(tags=("assets:list",))
async def delete_asset_document(
    request: Request,
    asset_id: UUID,
    document_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    """Удалить документ (каскадно удаляет все файлы)"""
    await service.delete_document(asset_id, document_id, actor)
    return StatusResponse(status="deleted", message="Asset document successfully deleted")
