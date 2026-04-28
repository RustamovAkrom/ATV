from uuid import UUID

from core.events.base import BaseEventService
from core.notifications.builder import NotificationBuilder
from core.notifications.dispatcher import NotificationDispatcher
from services.assets.asset_history_service import AssetHistoryService


class AssetEventService:
    """
    Asset domain events ONLY.
    """

    def __init__(
        self,
        base: BaseEventService,
        history: AssetHistoryService,
        notifications: NotificationDispatcher,
    ):
        self.base = base
        self.history = history
        self.notifications = notifications

    async def created(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        user_id: UUID | None,
        asset_name: str,
        status: str,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "created",
                f"Asset created with status '{status}'",
            ),
            audit_event="asset.created",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
            },
            notification=lambda: (
                self.notifications.dispatch(
                    NotificationBuilder.asset_created(
                        user_id=user_id,
                        asset_id=asset_id,
                        name=asset_name,
                    )
                )
                if user_id
                else None
            ),
        )

    async def updated(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        owner_id: UUID | None,
        asset_name: str,
        fields: list[str],
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "updated",
                f"Updated fields: {', '.join(sorted(fields))}",
            ),
            audit_event="asset.updated",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "fields": fields,
            },
            notification=lambda: (
                self.notifications.dispatch(
                    NotificationBuilder.asset_updated(
                        user_id=owner_id,
                        asset_id=asset_id,
                        name=asset_name,
                        fields=fields,
                    )
                )
                if owner_id
                else None
            ),
        )

    async def status_changed(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        owner_id: UUID | None,
        from_status: str,
        to_status: str,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "status_changed",
                f"Status changed from '{from_status}' to '{to_status}'",
            ),
            audit_event="asset.status_changed",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "from_status": from_status,
                "to_status": to_status,
            },
            notification=lambda: (
                self.notifications.dispatch(
                    NotificationBuilder.asset_status_changed(
                        user_id=owner_id,
                        asset_id=asset_id,
                        from_status=from_status,
                        to_status=to_status,
                    )
                )
                if owner_id
                else None
            ),
        )

    async def deleted(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        owner_id: UUID | None,
        asset_name: str,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "deleted",
                "Asset deleted",
            ),
            audit_event="asset.deleted",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
            },
            notification=lambda: (
                self.notifications.dispatch(
                    NotificationBuilder.asset_deleted(
                        user_id=owner_id,
                        asset_id=asset_id,
                        name=asset_name,
                    )
                )
                if owner_id
                else None
            ),
        )

    async def assigned(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        user_id: UUID,
        asset_name: str,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "assigned",
                f"Asset assigned to user {user_id}",
            ),
            audit_event="asset.assigned",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "user_id": str(user_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.asset_assigned(
                    user_id=user_id,
                    asset_id=asset_id,
                    asset_name=asset_name,
                )
            ),
        )

    async def unassigned(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        user_id: UUID | None,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "unassigned",
                f"Asset unassigned from user {user_id}",
            ),
            audit_event="asset.unassigned",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "user_id": str(user_id),
            },
            notification=(
                lambda: (
                    self.notifications.dispatch(
                        NotificationBuilder.asset_unassigned(
                            user_id=user_id,
                            asset_id=asset_id,
                        )
                    )
                    if user_id
                    else None
                )
            ),
        )
