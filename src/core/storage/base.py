from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class FileUploadResult(BaseModel):
    """Стандартизированный результат загрузки файла"""
    file_path: str              # Относительный путь к файлу
    public_url: str             # Публичный URL для доступа
    file_size: int              # Размер в байтах
    original_name: str          # Оригинальное имя файла
    stored_name: str            # Сгенерированное имя в хранилище
    mime_type: str | None = None
    metadata: dict | None = None


class BaseStorageStrategy(ABC):
    """Абстрактный класс для стратегий хранения файлов"""

    @abstractmethod
    async def save(
        self,
        file: Any,  # FastAPI UploadFile
        original_name: str,
        folder: str = "",
        metadata: dict | None = None,
    ) -> FileUploadResult:
        """
        Сохранить файл.

        Args:
            file: FastAPI UploadFile объект
            original_name: Оригинальное имя файла
            folder: Поддиректория для хранения
            metadata: Дополнительные метаданные

        Returns:
            FileUploadResult: Результат загрузки
        """
        pass

    @abstractmethod
    async def delete(self, file_path: str) -> bool:
        """
        Удалить файл.

        Args:
            file_path: Относительный путь к файлу

        Returns:
            bool: True если удалён, False если не найден
        """
        pass

    @abstractmethod
    async def exists(self, file_path: str) -> bool:
        """Проверить существование файла"""
        pass

    @abstractmethod
    async def get_absolute_path(self, file_path: str) -> str:
        """Получить абсолютный путь к файлу"""
        pass
