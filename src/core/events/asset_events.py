# core/events/asset_events.py
from uuid import UUID
from core.events.domain_event_service import DomainEventService
from core.notifications.builder import NotificationBuilder


class AssetEventService(DomainEventService):
    """Asset domain events."""

    async def created(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        user_id: UUID | None,
        asset_name: str,
        status: str,
    ):
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="created",
            description=f"Asset created with status '{status}'",
            audit_event="asset.created",
            audit_payload={"asset_id": str(asset_id), "actor_id": str(actor_id)},
            notification=lambda: (
                self.notifications.dispatch(
                    NotificationBuilder.asset_created(
                        user_id=user_id, asset_id=asset_id, name=asset_name
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
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="updated",
            description=f"Updated fields: {', '.join(sorted(fields))}",
            audit_event="asset.updated",
            audit_payload={"asset_id": str(asset_id), "actor_id": str(actor_id), "fields": fields},
            notification=lambda: (
                self.notifications.dispatch(
                    NotificationBuilder.asset_updated(
                        user_id=owner_id, asset_id=asset_id, name=asset_name, fields=fields
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
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="status_changed",
            description=f"Status changed from '{from_status}' to '{to_status}'",
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
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="deleted",
            description="Asset deleted",
            audit_event="asset.deleted",
            audit_payload={"asset_id": str(asset_id), "actor_id": str(actor_id)},
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
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="assigned",
            description=f"Asset assigned to user {user_id}",
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
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="unassigned",
            description=f"Asset unassigned from user {user_id}",
            audit_event="asset.unassigned",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "user_id": str(user_id),
            },
            notification=lambda: (
                self.notifications.dispatch(
                    NotificationBuilder.asset_unassigned(
                        user_id=user_id,
                        asset_id=asset_id,
                    )
                )
                if user_id
                else None
            ),
        )

    async def maintenance_performed(
        self,
        *,
        asset_id: UUID,
        actor_id: UUID,
        maintenance_type: str,
        performed_by_id: UUID,
    ):
        """Выполнено техническое обслуживание"""
        await self._execute(
            asset_id=asset_id,
            actor_id=actor_id,
            action="maintenance_performed",
            description=f"{maintenance_type} performed",
            audit_event="asset.maintenance_performed",
            audit_payload={
                "asset_id": str(asset_id),
                "actor_id": str(actor_id),
                "maintenance_type": maintenance_type,
                "performed_by_id": str(performed_by_id),
            },
            notification=None,
        )
