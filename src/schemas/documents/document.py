from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from core.config import get_settings
from db.models.enums import DocumentStatus
from schemas.base import BaseSchema, TimestampSchema

settings = get_settings()


class DocumentFileCreateSchema(BaseSchema):
    """Схема для создания файла документа"""

    file_name: str = Field(min_length=1, max_length=255)
    file_path: str = Field(min_length=1, max_length=500)
    file_size: int | None = Field(None, ge=0)
    content_type: str | None = Field(None, max_length=100)


class DocumentFileOutSchema(BaseSchema):
    """Схема для вывода файла документа"""

    id: UUID
    file_name: str
    file_path: str
    file_size: int | None
    content_type: str | None
    created_at: datetime | None = None
    url: str | None = None  # <-- явное поле

    def model_post_init(self, __context):
        """Вычисляем URL после инициализации модели"""
        if self.file_path:
            self.url = f"{settings.STORAGE_URL_PREFIX}/{self.file_path}"


class AssetDocumentCreateSchema(BaseSchema):
    """Схема для создания документа (JSON + файлы)"""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    document_type: str = Field(default="other", min_length=1, max_length=50)
    status: DocumentStatus = DocumentStatus.DRAFT
    metadata: dict = Field(default_factory=dict)


class AssetDocumentUpdateSchema(BaseSchema):
    """Схема для обновления документа"""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=500)
    document_type: str | None = Field(None, min_length=1, max_length=50)
    status: DocumentStatus | None = None
    metadata: dict | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is not None:
            cleaned = v.strip()
            if not cleaned:
                raise ValueError("Title cannot be empty")
            return cleaned
        return v


class AssetDocumentOutSchema(TimestampSchema):
    """Схема для вывода документа"""

    id: UUID
    title: str
    description: str | None
    document_type: str
    asset_id: UUID | None
    created_by_id: UUID
    status: DocumentStatus
    metadata: dict = Field(alias="meta")
    files: list[DocumentFileOutSchema] = Field(default_factory=list)
    created_by_name: str | None = None


class AssetDocumentWithFilesOutSchema(AssetDocumentOutSchema):
    """Document with full file information"""

    total_files_size: int | None = None
    file_count: int = 0

    def model_post_init(self, __context):
        """Вычисляем общий размер файлов после инициализации"""
        if self.files:
            self.total_files_size = sum(f.file_size or 0 for f in self.files)
            self.file_count = len(self.files)
