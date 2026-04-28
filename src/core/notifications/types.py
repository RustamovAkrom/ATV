from enum import StrEnum


class NotificationType(StrEnum):
    # assets
    ASSET_CREATED = "asset.created"
    ASSET_ASSIGNED = "asset.assigned"
    ASSET_UNASSIGNED = "asset.unassigned"
    ASSET_UPDATED = "asset.updated"
    ASSET_STATUS_CHANGED = "asset.status_changed"
    ASSET_DELETED = "asset.deleted"

    REPAIR_REPORTED = "repair.reported"
    REPAIR_STARTED = "repair.started"
    REPAIR_COMPLETED = "repair.completed"
    REPAIR_CANCELED = "repair.canceled"

    ASSET_TRANSFER_CREATED = "asset.transfer.created"
    ASSET_TRANSFER_COMPLETED = "asset.transfer.completed"
    ASSET_TRANSFER_REJECTED = "asset.transfer.rejected"

    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_EXECUTED = "approval.executed"
    APPROVAL_FAILED = "approval.failed"
    APPROVAL_CANCELED = "approval.canceled"
    APPROVAL_EXECUTION_FAILED = "approval.execution_failed"
