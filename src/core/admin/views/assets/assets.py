from core.admin.base import BaseAdmin
from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_category import AssetCategory
from db.models.assets.asset_class import AssetClass
from db.models.assets.asset_history import AssetHistory
from db.models.assets.asset_model import AssetModel
from db.models.assets.asset_transfer import AssetTransfer
from db.models.assets.manufacturer import Manufacturer
from db.models.warehouse.warehouse import Warehouse
import json
from wtforms import TextAreaField

class AssetAdmin(BaseAdmin, model=Asset):
    name = "Asset"
    name_plural = "Assets"
    icon = "fa-solid fa-box"

    can_edit = True
    can_create = True
    can_delete = True

    form_excluded_columns = ["meta"]

    column_list = [
        "id",
        "name",
        "type",
        "asset_tag",
        "serial_number",
        "status",
        "owner",
        "warehouse",
        "region",
        "service",
        "created_at",
    ]

    column_searchable_list = ["name", "asset_tag", "serial_number"]

    column_sortable_list = ["created_at", "name", "asset_tag"]

    column_formatters = {
        "owner": lambda m, _: m.owner.full_name if m.owner else None,
        "warehouse": lambda m, _: m.warehouse.name if m.warehouse else None,
        "region": lambda m, _: m.region.name if m.region else None,
        "service": lambda m, _: m.service.name if m.service else None,
        "meta": lambda m, _: json.dumps(m.meta, indent=2) if m.meta else "{}"
    }


class AssetAssignmentAdmin(BaseAdmin, model=AssetAssignment):
    name = "Asset Assignment"
    name_plural = "Asset Assignments"
    icon = "fa-solid fa-user-check"

    can_edit = True
    can_create = True
    can_delete = True

    column_list = [
        "id",
        "asset",
        "user",
        "assigned_at",
        "unassigned_at",
    ]

    column_formatters = {
        "asset": lambda m, _: m.asset.name if m.asset else None,
        "user": lambda m, _: m.user.full_name if m.user else None,
    }


class AssetCategoryAdmin(BaseAdmin, model=AssetCategory):
    name = "Asset Category"
    name_plural = "Asset Categories"
    icon = "fa-solid fa-tags"

    can_edit = True
    can_create = True
    can_delete = True

    column_list = ["id", "name", "slug", "created_at"]


class AssetClassAdmin(BaseAdmin, model=AssetClass):
    name = "Asset Class"
    name_plural = "Asset Classes"
    icon = "fa-solid fa-layer-group"

    can_edit = True
    can_create = True
    can_delete = True

    column_list = ["id", "name", "slug", "created_at"]


class AssetHistoryAdmin(BaseAdmin, model=AssetHistory):
    name = "Asset History"
    name_plural = "Asset Histories"
    icon = "fa-solid fa-history"

    column_list = [
        "id",
        "asset",
        "user",
        "action",
        "description",
        "created_at",
    ]

    column_formatters = {
        "asset": lambda m, _: m.asset.name if m.asset else None,
        "user": lambda m, _: m.user.full_name if m.user else None,
    }


class AssetModelAdmin(BaseAdmin, model=AssetModel):
    name = "Asset Model"
    name_plural = "Asset Models"
    icon = "fa-solid fa-cogs"

    column_list = [
        "id",
        "name",
        "slug",
        "manufacturer",
        "category",
        "lifetime_years",
        "warranty_months",
        "created_at",
    ]

    column_formatters = {
        "manufacturer": lambda m, _: m.manufacturer.name if m.manufacturer else None,
        "category": lambda m, _: m.category.name if m.category else None,
    }


class AssetTransferAdmin(BaseAdmin, model=AssetTransfer):
    name = "Asset Transfer"
    name_plural = "Asset Transfers"
    icon = "fa-solid fa-exchange-alt"

    column_list = [
        "id",
        "asset",
        "created_by",
        "from_warehouse",
        "to_warehouse",
        "status",
        "created_at",
    ]

    column_formatters = {
        "asset": lambda m, _: m.asset.name if m.asset else None,
        "created_by": lambda m, _: m.created_by.full_name if m.created_by else None,
        "from_warehouse": lambda m, _: m.from_warehouse.name if m.from_warehouse else None,
        "to_warehouse": lambda m, _: m.to_warehouse.name if m.to_warehouse else None,
    }


class ManufacturerAdmin(BaseAdmin, model=Manufacturer):
    name = "Manufacturer"
    name_plural = "Manufacturers"
    icon = "fa-solid fa-industry"

    column_list = ["id", "name", "slug", "created_at"]


class WarehouseAdmin(BaseAdmin, model=Warehouse):
    name = "Warehouse"
    name_plural = "Warehouses"
    icon = "fa-solid fa-warehouse"

    column_list = [
        "id",
        "name",
        "slug",
        "region",
        "service",
        "is_active",
        "created_at",
    ]

    column_formatters = {
        "region": lambda m, _: m.region.name if m.region else None,
        "service": lambda m, _: m.service.name if m.service else None,
    }
