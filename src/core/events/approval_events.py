# core/events/approval_events.py
from uuid import UUID

from core.events.domain_event_service import DomainEventService
from core.notifications.builder import NotificationBuilder


class ApprovalEventService(DomainEventService):
    """Approval domain events."""

    async def requested(
        self,
        *,
        approval_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: str,
        requester_id: UUID,
        approver_ids: list[UUID],
    ):
        """Notification about approval request creation."""
        for approver_id in approver_ids:
            await self._execute(
                asset_id=entity_id,  # entity_id это asset_id в большинстве случаев
                actor_id=requester_id,
                action="approval_requested",
                description=f"Approval requested for {entity_type}: {action}",
                audit_event="approval.requested",
                audit_payload={
                    "approval_id": str(approval_id),
                    "entity_type": entity_type,
                    "entity_id": str(entity_id),
                    "action": action,
                    "requester_id": str(requester_id),
                    "approver_id": str(approver_id),
                },
                notification=(
                    lambda approver_id=approver_id: self.notifications.dispatch(
                        NotificationBuilder.approval_requested(
                            user_id=approver_id,
                            entity_type=entity_type,
                            entity_id=entity_id,
                            action=action,
                        )
                    )
                ),
            )

    async def approved(
        self,
        *,
        approval_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: str,
        requester_id: UUID,
        approver_id: UUID,
    ):
        """Notification about request approval."""
        await self._execute(
            asset_id=entity_id,
            actor_id=approver_id,
            action="approval_approved",
            description=f"Approval {approval_id} approved by {approver_id}",
            audit_event="approval.approved",
            audit_payload={
                "approval_id": str(approval_id),
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
                "requester_id": str(requester_id),
                "approver_id": str(approver_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.approval_approved(
                    user_id=requester_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                )
            ),
        )

    async def rejected(
        self,
        *,
        approval_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: str,
        requester_id: UUID,
        approver_id: UUID,
        reason: str | None = None,
    ):
        """Notification about request rejection."""
        await self._execute(
            asset_id=entity_id,
            actor_id=approver_id,
            action="approval_rejected",
            description=f"Approval {approval_id} rejected by {approver_id}",
            audit_event="approval.rejected",
            audit_payload={
                "approval_id": str(approval_id),
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
                "requester_id": str(requester_id),
                "approver_id": str(approver_id),
                "reason": reason,
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.approval_rejected(
                    user_id=requester_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                )
            ),
        )

    async def executed(
        self,
        *,
        approval_id: UUID,
        entity_type: str,
        entity_id: UUID,
        action: str,
        requester_id: UUID,
    ):
        """Notification about successful execution of approved action."""
        await self._execute(
            asset_id=entity_id,
            actor_id=requester_id,
            action="approval_executed",
            description=f"Approved action executed: {action}",
            audit_event="approval.executed",
            audit_payload={
                "approval_id": str(approval_id),
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "action": action,
                "requester_id": str(requester_id),
            },
            notification=lambda: self.notifications.dispatch(
                NotificationBuilder.approval_executed(
                    user_id=requester_id,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    action=action,
                )
            ),
        )
