from uuid import UUID

import asyncpg
from sqlalchemy.exc import DBAPIError

from core.events.asset_events import AssetEventService
from core.exceptions.errors import BadRequest, NotFound
from core.security.access_control import AccessControl
from db.models.enums import AssetStatus, UserStatus
from repositories.assets.asset_assignment_repo import AssetAssignmentRepository
from schemas.assets.asset_assignments import AssetAssignmentActionSchema
from schemas.auth.auth import CurrentUserSchema
from utils.helpers import utc_now


class AssetAssignmentService:
    def __init__(
        self,
        repo: AssetAssignmentRepository,
        asset_events: AssetEventService,
    ):
        self.repo = repo
        self.asset_events = asset_events

    @staticmethod
    def _to_uuid(value: UUID | str | None) -> UUID | None:
        """Безопасное преобразование id в UUID"""
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        return UUID(str(value))

    async def assign_asset(
        self, asset_id: UUID, user_id: UUID, actor: CurrentUserSchema
    ) -> AssetAssignmentActionSchema:
        try:
            asset = await self.repo.get_asset_for_update(asset_id, nowait=True)
        except DBAPIError as e:
            if isinstance(e.orig, asyncpg.exceptions.LockNotAvailableError):
                raise BadRequest("Asset is locked") from e
            raise

        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        if asset.status == AssetStatus.ARCHIVED:
            raise BadRequest("Cannot assign archived asset")

        if asset.status == AssetStatus.IN_REPAIR:
            raise BadRequest("Cannot assign asset under repair")

        active_assignment = await self.repo.get_active_assignment(UUID(str(asset.id)))
        if active_assignment:
            if active_assignment.user_id == user_id:
                raise BadRequest("Asset is already assigned to this user")
            else:
                raise BadRequest("Asset already assigned")

        if asset.owner_id is not None:
            raise BadRequest("Asset already has owner (inconsistent state)")

        user = await self.repo.get_user(user_id)
        if not user:
            raise NotFound("User not found")

        if user.status != UserStatus.ACTIVE.value:
            raise BadRequest("Cannot assign asset to inactive user")

        if user.assigned_region_id and asset.region_id != user.assigned_region_id:
            raise BadRequest("User is assigned to a different region")

        if user.assigned_service_id and asset.service_id != user.assigned_service_id:
            raise BadRequest("User is assigned to a different service")

        asset.owner_id = UUID(str(user.id))
        asset.status = AssetStatus.ASSIGNED

        assignment = await self.repo.create_assignment(
            UUID(str(asset.id)), UUID(str(user.id))
        )

        await self.repo.flush()

        await self.asset_events.assigned(
            asset_id=UUID(str(asset.id)),
            user_id=UUID(str(user.id)),
            actor_id=UUID(str(actor.id)),
            asset_name=asset.name,
        )

        return AssetAssignmentActionSchema(
            asset_id=UUID(str(asset.id)),
            user_id=UUID(str(user.id)),
            assigned_at=assignment.assigned_at,
        )

    async def unassign_asset(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> AssetAssignmentActionSchema:

        asset = await self.repo.get_asset_for_update(asset_id)

        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        active_assignment = await self.repo.get_active_assignment(UUID(str(asset.id)))
        if not active_assignment:
            raise BadRequest("Asset is not currently assigned")

        timestamp = utc_now()
        previous_user_id = asset.owner_id

        await self.repo.close_assignment(active_assignment, timestamp)

        asset.owner_id = None
        asset.status = AssetStatus.ACTIVE

        if previous_user_id:
            await self.asset_events.unassigned(
                asset_id=UUID(str(asset.id)),
                actor_id=UUID(str(actor.id)),
                user_id=UUID(str(previous_user_id)),
            )

        return AssetAssignmentActionSchema(
            asset_id=UUID(str(asset.id)),
            user_id=UUID(str(previous_user_id)),
            unassigned_at=timestamp,
        )

    async def reassign_asset(
        self, asset_id: UUID, new_user_id: UUID, actor: CurrentUserSchema
    ) -> AssetAssignmentActionSchema:
        try:
            asset = await self.repo.get_asset_for_update(asset_id)
        except DBAPIError as e:
            raise BadRequest("Asset is locked") from e

        if not asset:
            raise BadRequest("Asset is locked or not available")

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        active_assignment = await self.repo.get_active_assignment(asset_id)

        if active_assignment:
            await self.repo.close_assignment(active_assignment, utc_now())

            asset.owner_id = None
            asset.status = AssetStatus.ACTIVE
            await self.repo.flush()

        return await self.assign_asset(asset_id, new_user_id, actor)

    async def get_active_assignment(
        self, asset_id: UUID
    ) -> AssetAssignmentActionSchema | None:
        """Получить активное назначение актива"""
        assignment = await self.repo.get_active_assignment(asset_id)
        if not assignment:
            return None

        return AssetAssignmentActionSchema(
            asset_id=assignment.asset_id,
            user_id=assignment.user_id,
            assigned_at=assignment.assigned_at,
            unassigned_at=assignment.unassigned_at,
        )
