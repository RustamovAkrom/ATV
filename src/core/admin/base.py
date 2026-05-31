from loguru import logger
from sqladmin import ModelView


class BaseAdmin(ModelView):
    """Base class for all admin models with security settings."""

    # Безопасность по умолчанию
    can_create = False  # Создание требует явного разрешения
    can_edit = False  # Редактирование требует явного разрешения
    can_delete = False  # Удаление требует явного разрешения
    can_view_details = True  # Просмотр обычно разрешён
    can_export = True  # Экспорт данных

    page_size = 50
    column_default_sort = ("id", True)

    # Дополнительные настройки
    save_as = True  # Возможность сохранить как новую запись
    save_as_continue = True  # После сохранения оставаться на форме

    # Настройки экспорта
    export_types = ["csv", "json", "xlsx"]

    # Скрыть чувствительные поля по умолчанию
    column_details_exclude_list = []
    column_form_exclude_list = []

    # Включить поиск
    searchable_columns = []

    @classmethod
    def is_accessible(cls, request) -> bool:
        """Check access to admin panel."""
        # Check if user is in session
        return "user" in request.session

    async def after_create(self, request, obj):
        """Логирование после создания."""
        logger.info(f"Admin created {self.__class__.__name__}: {obj}")

    async def after_edit(self, request, obj):
        """Логирование после редактирования."""
        logger.info(f"Admin edited {self.__class__.__name__}: {obj}")

    async def after_delete(self, request, obj):
        """Логирование после удаления."""
        logger.info(f"Admin deleted {self.__class__.__name__}: {obj}")
