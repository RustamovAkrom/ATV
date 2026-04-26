from enum import StrEnum


class NotificationType(StrEnum):
    # assets
    ASSET_CREATED = "asset.created"
    ASSET_ASSIGNED = "asset.assigned"
    ASSET_UPDATED = "asset.updated"
    ASSET_STATUS_CHANGED = "asset.status_changed"
    ASSET_DELETED = "asset.deleted"

    # approvals
    APPROVAL_APPROVED = "approval.approved"
    APPROVAL_REJECTED = "approval.rejected"

    # transfers
    ASSET_TRANSFER_CREATED = "asset.transfer.created"
    ASSET_TRANSFER_COMPLETED = "asset.transfer.completed"

    # repairs
    REPAIR_STARTED = "repair.started"
    REPAIR_COMPLETED = "repair.completed"
