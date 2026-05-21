# core/notifications/types.py
from enum import StrEnum


class NotificationType(StrEnum):
    # Assets
    ASSET_CREATED = "asset.created"
    ASSET_ASSIGNED = "asset.assigned"
    ASSET_UNASSIGNED = "asset.unassigned"
    ASSET_UPDATED = "asset.updated"
    ASSET_STATUS_CHANGED = "asset.status_changed"
    ASSET_DELETED = "asset.deleted"
    ASSET_MOVED_TO_WAREHOUSE = "asset.moved_to_warehouse"  # <-- ДОБАВИТЬ

    # Repairs
    REPAIR_REPORTED = "repair.reported"
    REPAIR_STARTED = "repair.started"
    REPAIR_COMPLETED = "repair.completed"
    REPAIR_CANCELED = "repair.canceled"

    # Transfers
    ASSET_TRANSFER_CREATED = "asset.transfer.created"
    ASSET_TRANSFER_COMPLETED = "asset.transfer.completed"
    ASSET_TRANSFER_REJECTED = "asset.transfer.rejected"

    # Approvals
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    APPROVAL_EXECUTED = "approval.executed"
    APPROVAL_EXECUTION_FAILED = "approval.execution_failed"
    APPROVAL_CANCELED = "approval.canceled"

    # Documents
    DOCUMENT_ATTACHED = "asset.document_attached"
    DOCUMENT_DELETED = "asset.document_deleted"
