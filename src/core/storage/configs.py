from .service import FileValidator


class UploadConfigs:
    """Готовые конфигурации для разных типов файлов"""

    @staticmethod
    def avatar() -> FileValidator:
        """Конфигурация для аватаров"""
        from core.config import get_settings
        settings = get_settings()
        return FileValidator(
            max_size_mb=settings.STORAGE_AVATAR_MAX_SIZE_MB,
            allowed_mimetypes=settings.STORAGE_AVATAR_ALLOWED_MIMETYPES,
        )

    @staticmethod
    def asset_image() -> FileValidator:
        """Конфигурация для изображений активов"""
        from core.config import get_settings
        settings = get_settings()
        return FileValidator(
            max_size_mb=settings.STORAGE_ASSET_IMAGE_MAX_SIZE_MB,
            allowed_mimetypes=settings.STORAGE_ASSET_IMAGE_ALLOWED_MIMETYPES,
        )

    @staticmethod
    def document() -> FileValidator:
        """Конфигурация для документов"""
        from core.config import get_settings
        settings = get_settings()
        return FileValidator(
            max_size_mb=settings.STORAGE_DOCUMENT_MAX_SIZE_MB,
            allowed_mimetypes=settings.STORAGE_DOCUMENT_ALLOWED_MIMETYPES,
        )

    @staticmethod
    def custom(
        max_size_mb: int,
        allowed_mimetypes: list[str],
        custom_validator=None,
    ) -> FileValidator:
        """Пользовательская конфигурация"""
        return FileValidator(
            max_size_mb=max_size_mb,
            allowed_mimetypes=allowed_mimetypes,
            custom_validator=custom_validator,
        )
