from core.admin.base import BaseAdmin
from db.models.users.permission import Role


class RoleAdmin(BaseAdmin, model=Role):
    name = "Role"
    name_plural = "Roles"
    icon = "fa-solid fa-user-tag"

    column_list = ["id", "name", "slug", "created_at"]

    form_excluded_columns = ["slug", "created_at", "updated_at"]
    can_edit = True
    can_create = True
    can_delete = True
