from functools import lru_cache

from core.storage import FileUploadService, LocalStorageStrategy


@lru_cache
def get_file_upload_service() -> FileUploadService:
    """Получить сервис для загрузки файлов"""
    storage = LocalStorageStrategy()
    return FileUploadService(storage)
