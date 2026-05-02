from core.admin.base import BaseAdmin
from db.models.users.permission import Role


class RoleAdmin(BaseAdmin, model=Role):
    name = "Role"
    name_plural = "Roles"
    icon = "fa-solid fa-user-tag"

    column_list = ["id", "name", "code", "created_at"]
