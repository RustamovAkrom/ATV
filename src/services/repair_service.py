from decimal import Decimal
from uuid import UUID

from core.audit.stream import audit_stream
from core.exceptions.errors import BadRequest, NotFound
from db.models.enums import AssetStatus, RepairStatus, UserStatus
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart
from repositories.repair_repo import RepairRepository
from schemas.repairs import (
    RepairCancelRequest,
    RepairCompleteRequest,
    RepairReportRequest,
    RepairSchema,
    RepairStartRequest,
)
from utils.helpers import utc_now


class RepairService:
    def __init__(self, repo: RepairRepository):
        self.repo = repo

    async def report_repair(
        self, asset_id: UUID, data: RepairReportRequest, actor_id: UUID
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        if asset.status != AssetStatus.ACTIVE:
            raise BadRequest("Repairs can only be reported for active assets")
        if await self.repo.get_active_repair(asset.id):
            raise BadRequest("Asset already has an active repair")

        repair = Repair(
            asset_id=asset.id,
            reported_by_id=actor_id,
            description=(data.description or "").strip() or None,
            status=RepairStatus.REPORTED,
        )
        await self.repo.create_repair(repair)
        await self.repo.add_history(
            asset.id, actor_id, "repair_reported", f"Repair {repair.id} reported"
        )
        await self._publish(
            "asset.repair_reported",
            {
                "asset_id": str(asset.id),
                "repair_id": str(repair.id),
                "actor_id": str(actor_id),
            },
        )
        return self._to_schema(repair)

    async def start_repair(
        self, asset_id: UUID, repair_id: UUID, data: RepairStartRequest, actor_id: UUID
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")
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
        asset.failure_count += 1
        if data.parts:
            await self.repo.replace_parts(
                repair, self._build_parts(repair.id, data.parts)
            )
        await self.repo.flush()

        await self.repo.add_history(
            asset.id, actor_id, "repair_started", f"Repair {repair.id} started"
        )
        await self._publish(
            "asset.repair_started",
            {
                "asset_id": str(asset.id),
                "repair_id": str(repair.id),
                "actor_id": str(actor_id),
            },
        )
        return self._to_schema(repair)

    async def complete_repair(
        self,
        asset_id: UUID,
        repair_id: UUID,
        data: RepairCompleteRequest,
        actor_id: UUID,
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        repair = await self.repo.get_repair_for_update(repair_id)
        if not repair or repair.asset_id != asset.id:
            raise NotFound("Repair not found")
        if repair.status != RepairStatus.IN_PROGRESS:
            raise BadRequest("Only in-progress repairs can be completed")

        if data.labor_cost is not None:
            repair.labor_cost = data.labor_cost
        if data.parts:
            await self.repo.replace_parts(
                repair, self._build_parts(repair.id, data.parts)
            )

        repair.status = RepairStatus.DONE
        repair.completed_at = utc_now()
        asset.status = AssetStatus.ACTIVE
        asset.last_repair_date = repair.completed_at.date()
        await self.repo.flush()

        await self.repo.add_history(
            asset.id, actor_id, "repair_completed", f"Repair {repair.id} completed"
        )
        await self._publish(
            "asset.repair_completed",
            {
                "asset_id": str(asset.id),
                "repair_id": str(repair.id),
                "actor_id": str(actor_id),
            },
        )
        return self._to_schema(repair)

    async def cancel_repair(
        self, asset_id: UUID, repair_id: UUID, data: RepairCancelRequest, actor_id: UUID
    ) -> RepairSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        repair = await self.repo.get_repair_for_update(repair_id)
        if not repair or repair.asset_id != asset.id:
            raise NotFound("Repair not found")
        if repair.status not in {RepairStatus.REPORTED, RepairStatus.IN_PROGRESS}:
            raise BadRequest("Repair cannot be canceled")

        repair.status = RepairStatus.CANCELED
        repair.completed_at = utc_now()
        if repair.started_at is not None:
            asset.status = AssetStatus.ACTIVE
        await self.repo.flush()

        reason = (data.reason or "").strip()
        message = f"Repair {repair.id} canceled"
        if reason:
            message = f"{message}: {reason}"
        await self.repo.add_history(asset.id, actor_id, "repair_canceled", message)
        await self._publish(
            "asset.repair_canceled",
            {
                "asset_id": str(asset.id),
                "repair_id": str(repair.id),
                "actor_id": str(actor_id),
            },
        )
        return self._to_schema(repair)

    def _to_schema(self, repair: Repair) -> RepairSchema:
        parts = list(repair.__dict__.get("parts") or [])
        total_cost = Decimal(repair.labor_cost or 0) + sum(
            Decimal(part.unit_price or 0) * part.quantity for part in parts
        )
        return RepairSchema(
            id=repair.id,
            asset_id=repair.asset_id,
            reported_by_id=repair.reported_by_id,
            assigned_to_id=repair.assigned_to_id,
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

    async def _publish(self, event: str, payload: dict) -> None:
        try:
            await audit_stream.publish(
                {"event": event, **payload, "timestamp": utc_now().timestamp()}
            )
        except Exception:
            return
