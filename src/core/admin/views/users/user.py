from core.admin.base import BaseAdmin
from db.models.users.user import User


class UserAdmin(BaseAdmin, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        "id",
        "login",
        "email",
        "phone",
        "full_name",
        "status",
        "role",
        "region",
        "service",
        "created_at",
        "updated_at",
    ]

    column_searchable_list = [
        "login",
        "email",
        "first_name",
        "last_name",
    ]

    column_sortable_list = [
        "created_at",
        "login",
        "email",
    ]

    column_formatters = {
        "role": lambda m, _: m.role.name if m.role else None,
        "region": lambda m, _: m.region.name if m.region else None,
        "service": lambda m, _: m.service.name if m.service else None,
    }

    column_formatters_detail = {
        "permissions": lambda m, _: ", ".join(m.permissions),
    }

    form_excluded_columns = [
        "owned_assets",
        "direct_permissions",
    ]
