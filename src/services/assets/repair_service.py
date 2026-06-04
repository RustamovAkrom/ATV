from datetime import datetime
from decimal import Decimal
from typing import Any, cast
from uuid import UUID

from core.events.repair_events import RepairEventService
from core.exceptions.errors import BadRequest, NotFound
from core.security.access_control import AccessControl
from db.models.enums import AssetStatus, RepairStatus, UserStatus
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart
from repositories.assets.repair_repo import RepairRepository
from schemas.assets.repairs import (
    RepairCancelRequest,
    RepairCompleteRequest,
    RepairReportRequest,
    RepairSchema,
    RepairStartRequest,
)
from schemas.auth.auth import CurrentUserSchema
from utils.helpers import utc_now


class RepairService:
    def __init__(
        self,
        repo: RepairRepository,
        repair_events: RepairEventService,
    ):
        self.repo = repo
        self.repair_events = repair_events

    @staticmethod
    def _to_uuid(value: Any) -> UUID:
        return cast(UUID, UUID(str(value)))

    async def report_repair(
        self, asset_id: UUID, data: RepairReportRequest, actor: CurrentUserSchema
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        if asset.status != AssetStatus.ACTIVE:
            raise BadRequest("Repairs can only be reported for active assets")

        active_assignment = await self.repo.get_active_assignment(
            self._to_uuid(asset.id)
        )
        if active_assignment:
            raise BadRequest("Cannot report repair for assigned asset")

        if await self.repo.get_active_repair(self._to_uuid(asset.id)):
            raise BadRequest("Asset already has an active repair")

        repair = Repair(
            asset_id=asset.id,
            reported_by_id=actor.id,
            description=(data.description or "").strip() or None,
            status=RepairStatus.REPORTED,
        )
        await self.repo.create_repair(repair)

        await self.repair_events.reported(
            asset_id=self._to_uuid(asset.id),
            repair_id=self._to_uuid(repair.id),
            actor_id=self._to_uuid(actor.id),
        )
        return self._to_schema(repair)

    async def start_repair(
        self,
        asset_id: UUID,
        repair_id: UUID,
        data: RepairStartRequest,
        actor: CurrentUserSchema,
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        existing = await self.repo.get_active_repair(self._to_uuid(asset.id))
        if existing and existing.id != repair_id:
            raise BadRequest("Another repair is already in progress for this asset")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        repair = await self.repo.get_repair_for_update(repair_id)

        if not repair or repair.asset_id != asset.id:
            raise NotFound("Repair not found")
        if repair.status != RepairStatus.REPORTED:
            raise BadRequest("Only reported repairs can be started")
        if asset.status != AssetStatus.ACTIVE:
            raise BadRequest("Only active assets can enter repair")

        if data.assigned_to_id is not None:
            user = await self.repo.get_user(data.assigned_to_id)
            if not user:
                raise BadRequest("Invalid assignee")
            if user.status != UserStatus.ACTIVE.value:
                raise BadRequest("Repair assignee must be active")

        repair.assigned_to_id = data.assigned_to_id
        repair.description = (
            data.description or repair.description or ""
        ).strip() or None
        repair.labor_cost = data.labor_cost
        repair.started_at = utc_now()
        repair.status = RepairStatus.IN_PROGRESS
        asset.status = AssetStatus.IN_REPAIR

        if data.parts:
            await self.repo.replace_parts(
                repair, self._build_parts(self._to_uuid(repair.id), data.parts)
            )
        await self.repo.flush()

        if repair.assigned_to_id:
            await self.repair_events.started(
                asset_id=self._to_uuid(asset.id),
                repair_id=self._to_uuid(repair.id),
                actor_id=self._to_uuid(actor.id),
                assigned_to_id=self._to_uuid(repair.assigned_to_id),
            )

        return self._to_schema(repair)

    async def complete_repair(
        self,
        asset_id: UUID,
        repair_id: UUID,
        data: RepairCompleteRequest,
        actor: CurrentUserSchema,
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        repair = await self.repo.get_repair_for_update(repair_id)
        if not repair or repair.asset_id != asset.id:
            raise NotFound("Repair not found")
        if repair.status != RepairStatus.IN_PROGRESS:
            raise BadRequest("Only in-progress repairs can be completed")

        if data.labor_cost is not None:
            repair.labor_cost = data.labor_cost
        if data.parts:
            await self.repo.replace_parts(
                repair, self._build_parts(self._to_uuid(repair.id), data.parts)
            )

        repair.status = RepairStatus.DONE
        completed_at: datetime = utc_now()
        repair.completed_at = completed_at
        asset.status = AssetStatus.ACTIVE
        asset.last_repair_date = completed_at.date()
        asset.failure_count += 1
        await self.repo.flush()

        if repair.reported_by_id:
            await self.repair_events.completed(
                asset_id=self._to_uuid(asset.id),
                repair_id=self._to_uuid(repair.id),
                actor_id=self._to_uuid(actor.id),
                reported_by_id=self._to_uuid(repair.reported_by_id),
            )

        return self._to_schema(repair)

    async def cancel_repair(
        self,
        asset_id: UUID,
        repair_id: UUID,
        data: RepairCancelRequest,
        actor: CurrentUserSchema,
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        repair = await self.repo.get_repair_for_update(repair_id)

        if not repair or repair.asset_id != asset.id:
            raise NotFound("Repair not found")

        if repair.status not in {RepairStatus.REPORTED, RepairStatus.IN_PROGRESS}:
            raise BadRequest("Repair cannot be canceled")

        repair.status = RepairStatus.CANCELED
        repair.completed_at = utc_now()
        asset.status = AssetStatus.ACTIVE

        await self.repo.flush()

        reason = (data.reason or "").strip()
        message = f"Repair {repair.id} canceled"
        if reason:
            message = f"{message}: {reason}"

        if repair.reported_by_id:
            await self.repair_events.canceled(
                asset_id=self._to_uuid(asset.id),
                repair_id=self._to_uuid(repair.id),
                actor_id=self._to_uuid(actor.id),
                reported_by_id=self._to_uuid(repair.reported_by_id),
                reason=data.reason,
            )

        return self._to_schema(repair)

    def _to_schema(self, repair: Repair) -> RepairSchema:
        parts = list(repair.__dict__.get("parts") or [])
        total_cost = Decimal(repair.labor_cost or 0) + sum(
            Decimal(part.unit_price or 0) * part.quantity for part in parts
        )
        return RepairSchema(
            id=self._to_uuid(repair.id),
            asset_id=self._to_uuid(repair.asset_id),
            reported_by_id=(
                self._to_uuid(repair.reported_by_id)
                if repair.reported_by_id is not None
                else None
            ),
            assigned_to_id=(
                self._to_uuid(repair.assigned_to_id)
                if repair.assigned_to_id is not None
                else None
            ),
            description=repair.description,
            status=repair.status,
            started_at=repair.started_at,
            completed_at=repair.completed_at,
            labor_cost=repair.labor_cost,
            total_cost=total_cost,
            parts=parts,
        )

    @staticmethod
    def _build_parts(repair_id: UUID, parts: list) -> list[RepairPart]:
        return [
            RepairPart(
                repair_id=repair_id,
                part_name=part.part_name,
                quantity=part.quantity,
                unit_price=part.unit_price,
            )
            for part in parts
        ]
