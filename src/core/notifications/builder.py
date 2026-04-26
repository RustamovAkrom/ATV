from uuid import UUID

from core.notifications.types import NotificationType


class NotificationBuilder:

    @staticmethod
    def asset_created(user_id: UUID, asset_id: UUID, name: str):
        return {
            "user_id": user_id,
            "type": NotificationType.ASSET_CREATED,
            "title": "Asset created",
            "message": f"Asset '{name}' created",
            "data": {"asset_id": str(asset_id)},
        }

    @staticmethod
    def asset_assigned(user_id: UUID, asset_id: UUID, name: str):
        return {
            "user_id": user_id,
            "type": NotificationType.ASSET_ASSIGNED,
            "title": "Asset assigned",
            "message": f"You have been assigned '{name}'",
            "data": {"asset_id": str(asset_id)},
        }

    @staticmethod
    def asset_status_changed(user_id: UUID, asset_id: UUID, from_status, to_status):
        return {
            "user_id": user_id,
            "type": NotificationType.ASSET_STATUS_CHANGED,
            "title": "Asset status changed",
            "message": f"Status changed from {from_status} → {to_status}",
            "data": {
                "asset_id": str(asset_id),
                "from": from_status,
                "to": to_status,
            },
        }

    @staticmethod
    def approval_approved(user_id: UUID):
        return {
            "user_id": user_id,
            "type": NotificationType.APPROVAL_APPROVED,
            "title": "Request approved",
            "message": "Your request has been approved",
            "data": {},
        }

    @staticmethod
    def approval_rejected(user_id: UUID):
        return {
            "user_id": user_id,
            "type": NotificationType.APPROVAL_REJECTED,
            "title": "Request rejected",
            "message": "Your request has been rejected",
            "data": {},
        }
