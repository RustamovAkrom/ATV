from collections.abc import Awaitable, Callable

from fastapi import HTTPException, UploadFile

from core.config import get_settings

from .base import BaseStorageStrategy, FileUploadResult

settings = get_settings()


class FileValidator:
    """Валидатор файлов"""

    def __init__(
        self,
        max_size_mb: int,
        allowed_mimetypes: list[str],
        custom_validator: Callable[[UploadFile], Awaitable[bool]] | None = None,
    ):
        self.max_size_mb = max_size_mb
        self.allowed_mimetypes = allowed_mimetypes
        self.custom_validator = custom_validator

    async def validate(self, file: UploadFile) -> None:
        """Проверить файл на соответствие требованиям"""
        max_size = self.max_size_mb * 1024 * 1024

        if file.size and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {self.max_size_mb}MB",
            )

        if file.content_type not in self.allowed_mimetypes:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed: {', '.join(self.allowed_mimetypes)}",
            )

        if self.custom_validator:
            if not await self.custom_validator(file):
                raise HTTPException(status_code=400, detail="Custom validation failed")


class FileUploadService:
    """Сервис для загрузки файлов"""

    def __init__(self, storage: BaseStorageStrategy):
        self.storage = storage

    async def upload(
        self,
        file: UploadFile,
        folder: str = "",
        validator: FileValidator | None = None,
        metadata: dict | None = None,
    ) -> FileUploadResult:
        """
        Загрузить файл.

        Args:
            file: Загружаемый файл
            folder: Поддиректория для хранения
            validator: Валидатор файла
            metadata: Метаданные

        Returns:
            FileUploadResult: Результат загрузки
        """
        if validator:
            await validator.validate(file)

        # Передаём UploadFile в storage
        return await self.storage.save(
            file=file,
            original_name=file.filename or "unknown",
            folder=folder,
            metadata=metadata,
        )

    async def delete(self, file_path: str) -> bool:
        """Удалить файл"""
        return await self.storage.delete(file_path)

    async def exists(self, file_path: str) -> bool:
        """Проверить существование файла"""
        return await self.storage.exists(file_path)
