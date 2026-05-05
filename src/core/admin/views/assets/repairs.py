from core.admin.base import BaseAdmin
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart


class RepairAdmin(BaseAdmin, model=Repair):
    name = "Repair"
    name_plural = "Repairs"
    icon = "fa-solid fa-wrench"

    column_list = [
        "id",
        "asset",
        "reported_by",
        "status",
        "labor_cost",
        "parts_cost",
        "started_at",
        "completed_at",
        "created_at",
    ]

    column_formatters = {
        "asset": lambda m, _: m.asset.name if m.asset else None,
        "reported_by": lambda m, _: m.reported_by.full_name if m.reported_by else None,
    }


class RepairPartAdmin(BaseAdmin, model=RepairPart):
    name = "Repair Part"
    name_plural = "Repair Parts"
    icon = "fa-solid fa-cogs"

    column_list = [
        "id",
        "repair",
        "part_name",
        "quantity",
        "unit_cost",
        "total_cost",
    ]

    column_formatters = {
        "repair": lambda m, _: f"Repair {m.repair.id}" if m.repair else None,
    }
