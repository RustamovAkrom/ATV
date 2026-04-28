from uuid import UUID
from typing import Any
from core.notifications.types import NotificationType


class NotificationBuilder:

    @staticmethod
    def _base(
        *,
        user_id: UUID,
        type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any],
    ):
        return {
            "user_id": user_id,
            "type": type.value,
            "title": title,
            "message": message,
            "data": data,
        }

    # Assets notifications
    @classmethod
    def asset_created(cls, *, user_id: UUID, asset_id: UUID, name: str):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_CREATED,
            title="Asset created",
            message=f"Asset '{name}' has been created",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_assigned(cls, *, user_id: UUID, asset_id: UUID, asset_name: str):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_ASSIGNED,
            title="Asset assigned",
            message=f"You have been assigned '{asset_name}'",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_unassigned(cls, *, user_id: UUID, asset_id: UUID):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_UNASSIGNED,
            title="Asset unassigned",
            message="Asset has been unassigned from you",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_status_changed(
        cls, *, user_id: UUID, asset_id: UUID, from_status: str, to_status: str
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_STATUS_CHANGED,
            title="Asset status changed",
            message=f"Status changed from {from_status} → {to_status}",
            data={
                "asset_id": str(asset_id),
                "from": from_status,
                "to": to_status,
            },
        )

    @classmethod
    def approval_approved(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.APPROVAL_APPROVED,
            title="Request approved",
            message=f"Your request has been approved: {entity_type} {action}",
            data={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
            },
        )

    @classmethod
    def approval_rejected(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.APPROVAL_REJECTED,
            title="Request rejected",
            message=f"Your request has been rejected: {entity_type} {action}",
            data={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
            },
        )

    @classmethod
    def asset_deleted(cls, *, user_id: UUID, asset_id: UUID, name: str):
        # Notify assigned user about asset deletion
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_DELETED,
            title="Asset deleted",
            message=f"Asset '{name}' has been deleted",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_updated(cls, *, user_id: UUID, asset_id: UUID, name: str):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_UPDATED,
            title="Asset updated",
            message=f"Asset '{name}' has been updated",
            data={"asset_id": str(asset_id)},
        )

    # Repairs notifications
    @classmethod
    def repair_reported(
        cls,
        *,
        user_id: UUID,
        asset_id: UUID,
        repair_id: UUID,
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.REPAIR_REPORTED,
            title="Repair reported",
            message="A repair request has been created",
            data={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
            },
        )

    @classmethod
    def repair_started(
        cls,
        *,
        user_id: UUID,
        asset_id: UUID,
        repair_id: UUID,
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.REPAIR_STARTED,
            title="Repair assigned",
            message="You have been assigned to a repair task",
            data={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
            },
        )

    @classmethod
    def repair_completed(
        cls,
        *,
        user_id: UUID,
        asset_id: UUID,
        repair_id: UUID,
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.REPAIR_COMPLETED,
            title="Repair completed",
            message="Repair has been successfully completed",
            data={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
            },
        )

    @classmethod
    def repair_canceled(
        cls,
        *,
        user_id: UUID,
        asset_id: UUID,
        repair_id: UUID,
        reason: str | None = None,
    ):
        message = "Repair has been canceled"
        if reason:
            message = f"{message}: {reason}"

        return cls._base(
            user_id=user_id,
            type=NotificationType.REPAIR_CANCELED,
            title="Repair canceled",
            message=message,
            data={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
            },
        )

    # Asset transfers notifications
    @classmethod
    def asset_transfer_created(
        cls, *, user_id: UUID, asset_id: UUID, transfer_id: UUID
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_TRANSFER_CREATED,
            title="Transfer created",
            message="Transfer request created",
            data={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
            },
        )

    @classmethod
    def asset_transfer_completed(
        cls, *, user_id: UUID, asset_id: UUID, transfer_id: UUID
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_TRANSFER_COMPLETED,
            title="Transfer completed",
            message="Transfer approved",
            data={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
            },
        )

    @classmethod
    def asset_transfer_rejected(
        cls, *, user_id: UUID, asset_id: UUID, transfer_id: UUID
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_TRANSFER_REJECTED,
            title="Transfer rejected",
            message="Transfer rejected",
            data={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
            },
        )

    # Approvals notifications
    @classmethod
    def approval_requested(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.APPROVAL_REQUESTED,
            title="Request created",
            message=f"You have a new request to approve: {entity_type} {action}",
            data={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
            },
        )

    @classmethod
    def approval_executed(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.APPROVAL_EXECUTED,
            title="Request executed",
            message=f"Your approved request has been executed: {entity_type} {action}",
            data={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
            },
        )

    @classmethod
    def approval_execution_failed(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.APPROVAL_EXECUTION_FAILED,
            title="Request execution failed",
            message=f"Execution of your approved request has failed: {entity_type} {action}",
            data={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
            },
        )

    @classmethod
    def approval_canceled(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ):
        return cls._base(
            user_id=user_id,
            type=NotificationType.APPROVAL_CANCELED,
            title="Request canceled",
            message=f"Your request has been canceled: {entity_type} {action}",
            data={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
            },
        )
