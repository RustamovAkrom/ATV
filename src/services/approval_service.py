from uuid import UUID

from core.exceptions.errors import BadRequest, NotFound
from db.models.approvals.approval_request import ApprovalRequest
from db.models.enums import ApprovalStatus, AssetStatus
from repositories.approval_repo import ApprovalRepository
from schemas.approvals import (
    ApprovalCreate,
    ApprovalSchema,
    AssetArchiveApprovalPayload,
    AssetDeleteApprovalPayload,
    RepairCompleteApprovalPayload,
)
from fastapi.encoders import jsonable_encoder

from schemas.asset_transfers import AssetTransferCreate
from schemas.assets import AssetStatusChangeRequest
from schemas.repairs import RepairCompleteRequest
from utils.helpers import utc_now


class ApprovalService:
    def __init__(
        self,
        approval_repo: ApprovalRepository,
        asset_service,
        transfer_service,
        repair_service,
    ):
        self.approval_repo = approval_repo
        self.asset_service = asset_service
        self.transfer_service = transfer_service
        self.repair_service = repair_service

    async def create(self, data: ApprovalCreate, actor_id: UUID) -> ApprovalSchema:
        validated_payload = self._validate_request(data)
        approval = ApprovalRequest(
            entity_type=data.entity_type.strip(),
            entity_id=data.entity_id,
            action=data.action.strip(),
            payload=validated_payload,
            status=ApprovalStatus.PENDING,
            created_by_id=actor_id,
            executed=False,
        )
        await self.approval_repo.create(approval)
        return ApprovalSchema.model_validate(approval, from_attributes=True)

    async def list(self) -> list[ApprovalSchema]:
        items = await self.approval_repo.list()
        return [ApprovalSchema.model_validate(item, from_attributes=True) for item in items]

    async def approve(self, approval_id: UUID, actor_id: UUID, comment: str | None = None) -> ApprovalSchema:
        async with self.approval_repo.session.begin_nested():
            approval = await self._get_pending(approval_id, for_update=True)
            await self._execute_approved_action(approval, actor_id, comment)
            approval.status = ApprovalStatus.APPROVED
            approval.approved_by_id = actor_id
            approval.executed = True
            approval.decided_at = utc_now()
            if comment:
                approval.payload = {**approval.payload, "approval_comment": comment.strip()}
            await self.approval_repo.flush()
        return ApprovalSchema.model_validate(approval, from_attributes=True)

    async def reject(self, approval_id: UUID, actor_id: UUID, comment: str | None = None) -> ApprovalSchema:
        async with self.approval_repo.session.begin_nested():
            approval = await self._get_pending(approval_id, for_update=True)
            approval.status = ApprovalStatus.REJECTED
            approval.approved_by_id = actor_id
            approval.decided_at = utc_now()
            if comment:
                approval.payload = {**approval.payload, "rejection_comment": comment.strip()}
            await self.approval_repo.flush()
        return ApprovalSchema.model_validate(approval, from_attributes=True)

    async def _get_pending(self, approval_id: UUID, for_update: bool = False) -> ApprovalRequest:
        approval = await (
            self.approval_repo.get_by_id_for_update(approval_id)
            if for_update
            else self.approval_repo.get_by_id(approval_id)
        )
        if not approval:
            raise NotFound("Approval request not found")
        if approval.status != ApprovalStatus.PENDING:
            raise BadRequest("Approval request has already been decided")
        if approval.executed:
            raise BadRequest("Approval request has already been executed")
        return approval

    def _validate_request(self, data: ApprovalCreate) -> dict:
        supported = {
            ("asset_transfer", "create_transfer"),
            ("asset_archive", "archive"),
            ("asset_delete", "delete"),
            ("repair", "complete_repair"),
        }
        key = (data.entity_type.strip(), data.action.strip())
        if key not in supported:
            raise BadRequest("Unsupported approval request")
        try:
            if key == ("asset_transfer", "create_transfer"):
                return jsonable_encoder(AssetTransferCreate(**data.payload).model_dump(exclude_none=True))
            if key == ("asset_archive", "archive"):
                return jsonable_encoder(AssetArchiveApprovalPayload(**data.payload).model_dump(exclude_none=True))
            if key == ("asset_delete", "delete"):
                return jsonable_encoder(AssetDeleteApprovalPayload(**data.payload).model_dump(exclude_none=True))
            if key == ("repair", "complete_repair"):
                return jsonable_encoder(RepairCompleteApprovalPayload(**data.payload).model_dump(exclude_none=True))
        except Exception as exc:
            raise BadRequest(f"Invalid approval payload: {exc}") from exc
        raise BadRequest("Unsupported approval request")

    async def _execute_approved_action(self, approval: ApprovalRequest, actor_id: UUID, comment: str | None) -> None:
        payload = dict(approval.payload or {})
        if approval.entity_type == "asset_transfer" and approval.action == "create_transfer":
            await self.transfer_service.create_transfer(
                approval.entity_id,
                AssetTransferCreate(**payload),
                actor_id,
            )
            return
        if approval.entity_type == "asset_archive" and approval.action == "archive":
            await self.asset_service.change_status(
                approval.entity_id,
                AssetStatusChangeRequest(status=AssetStatus.ARCHIVED),
                actor_id,
            )
            return
        if approval.entity_type == "asset_delete" and approval.action == "delete":
            await self.asset_service.delete(approval.entity_id, actor_id)
            return
        if approval.entity_type == "repair" and approval.action == "complete_repair":
            repair_id_raw = payload.get("repair_id")
            if not repair_id_raw:
                raise BadRequest("Repair approval payload requires repair_id")
            repair_id = UUID(str(repair_id_raw))
            complete_payload = {k: v for k, v in payload.items() if k != "repair_id"}
            await self.repair_service.complete_repair(
                approval.entity_id,
                repair_id,
                RepairCompleteRequest(**complete_payload),
                actor_id,
            )
            return
        raise BadRequest("Unsupported approval execution")
