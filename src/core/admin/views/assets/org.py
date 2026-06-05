from core.admin.base import BaseAdmin
from db.models.org.department import Department
from db.models.org.region import Region
from db.models.org.service import Service


class DepartmentAdmin(BaseAdmin, model=Department):
    name = "Department"
    name_plural = "Departments"

    can_edit = True
    can_create = True
    can_delete = True

    column_list = [
        "id",
        "name",
        "description",
        "is_active",
    ]

    form_excluded_columns = ["slug", "created_at", "updated_at", "meta"]

class RegionAdmin(BaseAdmin, model=Region):
    name = "Region"
    name_plural = "Regions"
    icon = "fa-solid fa-map"

    can_edit = True
    can_create = True
    can_delete = True

    column_list = [
        "id",
        "name",
        "latitude",
        "longitude",
        "geojson",
        "created_at",
    ]

    form_excluded_columns = ["slug", "created_at", "updated_at"]


class ServiceAdmin(BaseAdmin, model=Service):
    name = "Service"
    name_plural = "Services"
    icon = "fa-solid fa-cogs"

    can_edit = True
    can_create = True
    can_delete = True

    column_list = ["id", "name", "slug", "created_at"]

    form_excluded_columns = ["slug", "created_at", "updated_at"]
