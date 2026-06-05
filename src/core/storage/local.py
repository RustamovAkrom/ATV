import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from core.config import get_settings

from .base import BaseStorageStrategy, FileUploadResult

settings = get_settings()
STORAGE_URL = settings.BACKEND_DOMAIN + settings.STORAGE_URL

class LocalStorageStrategy(BaseStorageStrategy):
    """Локальное хранилище файлов"""

    def __init__(self, base_path: Path | None = None):
        self.base_path = base_path or settings.BASE_DIR / settings.STORAGE_ROOT_DIR
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _generate_stored_name(self, original_name: str) -> str:
        """Генерирует безопасное имя для хранения"""
        ext = Path(original_name).suffix.lower()

        if settings.STORAGE_KEEP_ORIGINAL_NAME:
            # Очищаем оригинальное имя от опасных символов
            safe_name = "".join(c for c in original_name if c.isalnum() or c in "._-")
            if len(safe_name) > settings.STORAGE_FILENAME_MAX_LENGTH:
                safe_name = safe_name[: settings.STORAGE_FILENAME_MAX_LENGTH - 8]
            return f"{safe_name}_{uuid.uuid4().hex[:8]}{ext}"

        return f"{uuid.uuid4().hex}{ext}"

    async def save(
        self,
        file: UploadFile,
        original_name: str,
        folder: str = "",
        metadata: dict | None = None,
    ) -> FileUploadResult:
        """Сохранить файл локально"""
        # Генерируем имена
        stored_name = self._generate_stored_name(original_name)
        relative_path = Path(folder) / stored_name if folder else Path(stored_name)
        full_path = self.base_path / relative_path

        # Создаём директорию если нужно
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Сохраняем файл
        try:
            content = await file.read()  # Читаем асинхронно
            async with aiofiles.open(full_path, "wb") as buffer:
                await buffer.write(content)
        except Exception as e:
            raise RuntimeError(f"Failed to save file: {e}") from e

        # Формируем публичный URL
        public_url = f"{STORAGE_URL}/{relative_path.as_posix()}"

        return FileUploadResult(
            file_path=relative_path.as_posix(),
            public_url=public_url,
            file_size=full_path.stat().st_size,
            original_name=original_name,
            stored_name=stored_name,
            metadata=metadata,
        )

    async def delete(self, file_path: str) -> bool:
        """Удалить файл"""
        full_path = self.base_path / file_path
        if full_path.exists() and full_path.is_file():
            full_path.unlink()
            return True
        return False

    async def exists(self, file_path: str) -> bool:
        """Проверить существование файла"""
        full_path = self.base_path / file_path
        return full_path.exists() and full_path.is_file()

    async def get_absolute_path(self, file_path: str) -> str:
        """Получить абсолютный путь к файлу"""
        return str(self.base_path / file_path)
