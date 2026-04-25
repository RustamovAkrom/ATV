from uuid import UUID

import asyncpg
from sqlalchemy.exc import DBAPIError

from core.audit.stream import audit_stream
from core.exceptions.errors import BadRequest, NotFound
from db.models.enums import AssetStatus, UserStatus
from repositories.asset_assignment_repo import AssetAssignmentRepository
from schemas.asset_assignments import AssetAssignmentActionSchema
from utils.helpers import utc_now


class AssetAssignmentService:
    def __init__(self, repo: AssetAssignmentRepository):
        self.repo = repo

    async def assign_asset(
        self, asset_id: UUID, user_id: UUID, actor_id: UUID
    ) -> AssetAssignmentActionSchema:
        try:
            asset = await self.repo.get_asset_for_update(asset_id, nowait=True)
        except DBAPIError as e:
            if isinstance(e.orig, asyncpg.exceptions.LockNotAvailableError):
                raise BadRequest("Asset is locked")
            raise

        if not asset:
            raise NotFound("Asset not found")

        if asset.status == AssetStatus.ARCHIVED:
            raise BadRequest("Cannot assign archived asset")

        user = await self.repo.get_user(user_id)
        if not user:
            raise NotFound("User not found")
        if user.status != UserStatus.ACTIVE.value:
            raise BadRequest("Cannot assign asset to inactive user")

        active_assignment = await self.repo.get_active_assignment(asset.id)
        if active_assignment:
            if active_assignment.user_id == user.id:
                raise BadRequest("Asset is already assigned to this user")
            raise BadRequest("Asset already assigned")

        asset.owner_id = user.id
        asset.status = AssetStatus.ASSIGNED
        await self.repo.flush()

        assignment = await self.repo.create_assignment(asset.id, user.id)
        await self.repo.add_history(
            asset.id, actor_id, "assigned", f"Asset assigned to user {user.id}"
        )
        await self._publish(
            "asset.assigned",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor_id),
                "user_id": str(user.id),
            },
        )
        return AssetAssignmentActionSchema(
            asset_id=asset.id,
            user_id=user.id,
            assigned_at=assignment.assigned_at,
        )

    async def unassign_asset(
        self, asset_id: UUID, actor_id: UUID
    ) -> AssetAssignmentActionSchema:
        try:
            asset = await self.repo.get_asset_for_update(asset_id)
        except DBAPIError:
            raise BadRequest("Asset is locked")

        if not asset:
            asset = await self.repo.get_asset_plain(asset_id)

        if not asset:
            raise NotFound("Asset not found")

        active_assignment = await self.repo.get_active_assignment(asset.id)
        if not active_assignment:
            raise BadRequest("Asset is not currently assigned")

        timestamp = utc_now()
        await self.repo.close_assignment(active_assignment, timestamp)
        previous_user_id = asset.owner_id
        asset.owner_id = None
        asset.status = AssetStatus.ACTIVE
        await self.repo.flush()

        await self.repo.add_history(
            asset.id,
            actor_id,
            "unassigned",
            f"Asset unassigned from user {previous_user_id}",
        )
        await self._publish(
            "asset.unassigned",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor_id),
                "user_id": str(previous_user_id),
            },
        )
        return AssetAssignmentActionSchema(
            asset_id=asset.id,
            user_id=previous_user_id,
            unassigned_at=timestamp,
        )

    async def reassign_asset(
        self, asset_id: UUID, new_user_id: UUID, actor_id: UUID
    ) -> AssetAssignmentActionSchema:
        try:
            asset = await self.repo.get_asset_for_update(asset_id)
        except DBAPIError:
            raise BadRequest("Asset is locked")

        if not asset:
            raise BadRequest("Asset is locked or not available")

        active_assignment = await self.repo.get_active_assignment(asset_id)

        if active_assignment:
            await self.repo.close_assignment(active_assignment, utc_now())

        return await self.assign_asset(asset_id, new_user_id, actor_id)

    async def _publish(self, event: str, payload: dict) -> None:
        try:
            await audit_stream.publish(
                {"event": event, **payload, "timestamp": utc_now().timestamp()}
            )
        except Exception:
            return
