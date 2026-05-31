# core/notifications/builder.py
from typing import Any
from uuid import UUID

from core.notifications.types import NotificationType


class NotificationBuilder:
    """
    Билдер для создания уведомлений.
    Использует единый _base метод и фабричные методы для каждого типа.
    """

    @staticmethod
    def _base(
        *,
        user_id: UUID,
        type: NotificationType,
        title: str,
        message: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Базовый метод для создания уведомления."""
        return {
            "user_id": user_id,
            "type": type.value,
            "title": title,
            "message": message,
            "data": data,
        }

    # ==================== ASSET NOTIFICATIONS ====================

    @classmethod
    def asset_created(
        cls, *, user_id: UUID, asset_id: UUID, name: str
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_CREATED,
            title="Asset created",
            message=f"Asset '{name}' has been created",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_assigned(
        cls, *, user_id: UUID, asset_id: UUID, asset_name: str
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_ASSIGNED,
            title="Asset assigned",
            message=f"You have been assigned '{asset_name}'",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_unassigned(cls, *, user_id: UUID, asset_id: UUID) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_UNASSIGNED,
            title="Asset unassigned",
            message="Asset has been unassigned from you",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_updated(
        cls,
        *,
        user_id: UUID,
        asset_id: UUID,
        name: str,
        fields: list[str] | None = None,
    ) -> dict[str, Any]:
        data = {"asset_id": str(asset_id)}
        if fields:
            data["fields"] = fields  # type: ignore
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_UPDATED,
            title="Asset updated",
            message=f"Asset '{name}' has been updated",
            data=data,
        )

    @classmethod
    def asset_status_changed(
        cls, *, user_id: UUID, asset_id: UUID, from_status: str, to_status: str
    ) -> dict[str, Any]:
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
    def asset_deleted(
        cls, *, user_id: UUID, asset_id: UUID, name: str
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_DELETED,
            title="Asset deleted",
            message=f"Asset '{name}' has been deleted",
            data={"asset_id": str(asset_id)},
        )

    @classmethod
    def asset_moved_to_warehouse(
        cls,
        *,
        user_id: UUID,
        asset_id: UUID,
        warehouse_id: UUID,
        warehouse_name: str | None = None,
    ) -> dict[str, Any]:
        """Notification about asset moved to warehouse."""
        warehouse_display = warehouse_name or str(warehouse_id)
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_MOVED_TO_WAREHOUSE,
            title="Asset moved to warehouse",
            message=f"Asset has been moved to warehouse '{warehouse_display}'",
            data={
                "asset_id": str(asset_id),
                "warehouse_id": str(warehouse_id),
                "warehouse_name": warehouse_name,
            },
        )

    # ==================== REPAIR NOTIFICATIONS ====================

    @classmethod
    def repair_reported(
        cls, *, user_id: UUID, asset_id: UUID, repair_id: UUID
    ) -> dict[str, Any]:
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
        cls, *, user_id: UUID, asset_id: UUID, repair_id: UUID
    ) -> dict[str, Any]:
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
        cls, *, user_id: UUID, asset_id: UUID, repair_id: UUID
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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
                "reason": reason,
            },
        )

    # ==================== TRANSFER NOTIFICATIONS ====================

    @classmethod
    def asset_transfer_created(
        cls, *, user_id: UUID, asset_id: UUID, transfer_id: UUID
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_TRANSFER_COMPLETED,
            title="Transfer completed",
            message="Transfer has been completed",
            data={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
            },
        )

    @classmethod
    def asset_transfer_rejected(
        cls, *, user_id: UUID, asset_id: UUID, transfer_id: UUID
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.ASSET_TRANSFER_REJECTED,
            title="Transfer rejected",
            message="Transfer request has been rejected",
            data={
                "asset_id": str(asset_id),
                "transfer_id": str(transfer_id),
            },
        )

    # ==================== APPROVAL NOTIFICATIONS ====================

    @classmethod
    def approval_requested(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ) -> dict[str, Any]:
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
    def approval_approved(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
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
    def approval_executed(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ) -> dict[str, Any]:
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
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.APPROVAL_EXECUTION_FAILED,
            title="Request execution failed",
            message=(
                "Execution of your approved request has failed: "
                f"{entity_type} {action.lower()}"
            ),
            data={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
            },
        )

    @classmethod
    def approval_canceled(
        cls, *, user_id: UUID, entity_type: str, entity_id: UUID, action: str
    ) -> dict[str, Any]:
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

    # ==================== DOCUMENT NOTIFICATIONS ====================

    @classmethod
    def document_attached(
        cls, *, user_id: UUID, asset_id: UUID, document_id: UUID
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.DOCUMENT_ATTACHED,
            title="Document attached",
            message="A document has been attached to the asset",
            data={
                "asset_id": str(asset_id),
                "document_id": str(document_id),
            },
        )

    @classmethod
    def document_deleted(
        cls, *, user_id: UUID, asset_id: UUID, document_id: UUID
    ) -> dict[str, Any]:
        return cls._base(
            user_id=user_id,
            type=NotificationType.DOCUMENT_DELETED,
            title="Document deleted",
            message="A document has been removed from the asset",
            data={
                "asset_id": str(asset_id),
                "document_id": str(document_id),
            },
        )
