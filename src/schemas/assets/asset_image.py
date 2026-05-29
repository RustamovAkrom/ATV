from uuid import UUID

from pydantic import Field

from schemas.base import BaseSchema, TimestampSchema


class AssetImageCreateSchema(BaseSchema):
    """Создание изображения актива"""

    file_name: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(gt=0, le=10 * 1024 * 1024)  # max 10MB
    content_type: str = Field(max_length=100)
    width: int | None = Field(None, ge=1)
    height: int | None = Field(None, ge=1)
    alt_text: str | None = Field(None, max_length=255)


class AssetImageUpdateSchema(BaseSchema):
    """Обновление изображения актива"""

    is_primary: bool | None = None
    sort_order: int | None = Field(None, ge=0)
    alt_text: str | None = Field(None, max_length=255)


class AssetImageOutSchema(TimestampSchema):
    """Вывод изображения актива"""

    id: UUID
    asset_id: UUID
    file_name: str
    file_path: str
    file_size: int
    content_type: str
    is_primary: bool
    sort_order: int
    width: int | None
    height: int | None
    alt_text: str | None
    url: str | None = None

    def model_post_init(self, __context):
        """Вычисляем URL после инициализации модели"""
        if self.id:
            # Генерируем URL для доступа к изображению через API
            self.url = f"/assets/{self.asset_id}/images/file/{self.id}"
