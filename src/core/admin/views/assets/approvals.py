from core.admin.base import BaseAdmin
from db.models.approvals.approval_request import ApprovalRequest


class ApprovalRequestAdmin(BaseAdmin, model=ApprovalRequest):
    name = "Approval Request"
    name_plural = "Approval Requests"
    icon = "fa-solid fa-check-circle"

    column_list = [
        "id",
        "created_by",
        "approved_by",
        "entity_type",
        "entity_id",
        "action",
        "status",
        "executed",
        "decided_at",
        "created_at",
        "updated_at",
    ]

    column_formatters = {
        "created_by": lambda m, _: m.created_by.full_name if m.created_by else None,
        "approved_by": lambda m, _: m.approved_by.full_name if m.approved_by else None,
    }
