from uuid import UUID

from core.events.domain_event_service import DomainEventService
from core.notifications.builder import NotificationBuilder


class RepairEventService(DomainEventService):
    async def reported(self, *, asset_id: UUID, repair_id: UUID, actor_id: UUID):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "repair_reported",
                f"Repair {repair_id} reported",
            ),
            audit_event="asset.repair_reported",
            audit_payload={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
                "actor_id": str(actor_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.repair_reported(
                    user_id=actor_id,
                    asset_id=asset_id,
                    repair_id=repair_id,
                )
            ),
        )

    async def started(
        self,
        *,
        asset_id: UUID,
        repair_id: UUID,
        actor_id: UUID,
        assigned_to_id: UUID | None,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "repair_started",
                f"Repair {repair_id} started",
            ),
            audit_event="asset.repair_started",
            audit_payload={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
                "actor_id": str(actor_id),
            },
            notification=(
                lambda: (
                    self.notifications.dispatch(
                        NotificationBuilder.repair_started(
                            user_id=assigned_to_id,
                            asset_id=asset_id,
                            repair_id=repair_id,
                        )
                    )
                    if assigned_to_id
                    else None
                )
            ),
        )

    async def completed(
        self,
        *,
        asset_id: UUID,
        repair_id: UUID,
        actor_id: UUID,
        reported_by_id: UUID | None,
    ):
        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "repair_completed",
                f"Repair {repair_id} completed",
            ),
            audit_event="asset.repair_completed",
            audit_payload={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
                "actor_id": str(actor_id),
            },
            notification=(
                lambda: (
                    self.notifications.dispatch(
                        NotificationBuilder.repair_completed(
                            user_id=reported_by_id,
                            asset_id=asset_id,
                            repair_id=repair_id,
                        )
                    )
                    if reported_by_id
                    else None
                )
            ),
        )

    async def canceled(
        self,
        *,
        asset_id: UUID,
        repair_id: UUID,
        actor_id: UUID,
        reported_by_id: UUID | None,
        reason: str | None,
    ):
        message = f"Repair {repair_id} canceled"
        if reason:
            message = f"{message}: {reason}"

        await self.base.execute(
            history=lambda: self.history.log(
                asset_id,
                actor_id,
                "repair_canceled",
                message,
            ),
            audit_event="asset.repair_canceled",
            audit_payload={
                "asset_id": str(asset_id),
                "repair_id": str(repair_id),
                "actor_id": str(actor_id),
            },
            notification=(
                lambda: (
                    self.notifications.dispatch(
                        NotificationBuilder.repair_canceled(
                            user_id=reported_by_id,
                            asset_id=asset_id,
                            repair_id=repair_id,
                            reason=reason,
                        )
                    )
                    if reported_by_id
                    else None
                )
            ),
        )
