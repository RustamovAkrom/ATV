from core.admin.base import BaseAdmin
from db.models.users.permission import Permission


class PermissionAdmin(BaseAdmin, model=Permission):
    name = "Permission"
    name_plural = "Permissions"
    icon = "fa-solid fa-dashboard"

    column_list = ["name"]
