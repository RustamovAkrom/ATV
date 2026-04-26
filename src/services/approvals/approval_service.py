# services/assets/approval_service.py

from uuid import UUID

from fastapi.encoders import jsonable_encoder

from core.exceptions.errors import BadRequest, NotFound, PermissionDenied
from db.models.approvals.approval_request import ApprovalRequest
from db.models.enums import ApprovalStatus, AssetStatus
from repositories.assets.approval_repo import ApprovalRepository
from schemas.assets.approvals import (
    ApprovalCreate,
    ApprovalSchema,
    AssetArchiveApprovalPayload,
    AssetDeleteApprovalPayload,
    RepairCompleteApprovalPayload,
)
from schemas.assets.asset_transfers import AssetTransferCreate
from schemas.assets.assets import AssetStatusChangeRequest
from schemas.assets.repairs import RepairCompleteRequest
from utils.helpers import utc_now
from schemas.pagination import PaginationParamsSchema, PageOutSchema, build_page
from schemas.auth.auth import CurrentUserSchema
from core.security.rbac.permissions import Permissions
from core.security.rbac.guards import check_permissions
from core.security.access_control import AccessControl
from services.assets.asset_service import AssetService
from services.assets.repair_service import RepairService
from services.assets.asset_transfer_service import AssetTransferService
from services.assets.asset_assignment_service import AssetAssignmentService
from core.notifications.builder import NotificationBuilder
from core.notifications.dispatcher import NotificationDispatcher

class ApprovalService:
    def __init__(
        self,
        approval_repo: ApprovalRepository,
        asset_service: AssetService,
        transfer_service: AssetTransferService,
        repair_service: RepairService,
        asset_assignment_service: AssetAssignmentService,
        notification_dispatcher: NotificationDispatcher,
    ):
        self.approval_repo = approval_repo
        self.asset_service = asset_service
        self.transfer_service = transfer_service
        self.repair_service = repair_service
        self.asset_assignment_service = asset_assignment_service
        self.notification_dispatcher = notification_dispatcher

    async def list(
        self,
        status: ApprovalStatus | None,
        pagination: PaginationParamsSchema,
    ):
        items, total = await self.approval_repo.list(status, pagination)

        return build_page(
                schema=PageOutSchema[ApprovalSchema],
                items=[
                    ApprovalSchema.model_validate(i, from_attributes=True)
                    for i in items
                ],
                total=total,
                page=pagination.page,
                limit=pagination.limit,
            )

    async def create(self, data: ApprovalCreate, actor: CurrentUserSchema) -> ApprovalSchema:
        validated_payload = self._validate_request(data)

        approval = ApprovalRequest(
            entity_type=data.entity_type.strip(),
            entity_id=data.entity_id,
            action=data.action.strip(),
            payload=validated_payload,
            status=ApprovalStatus.PENDING,
            created_by_id=actor.id,
            executed=False,
        )

        await self.approval_repo.create(approval)
        return ApprovalSchema.model_validate(approval, from_attributes=True)

    async def approve(
        self, approval_id: UUID, actor: CurrentUserSchema, comment: str | None = None
    ) -> ApprovalSchema:
        check_permissions(actor, Permissions.APPROVALS_APPROVE)

        async with self.approval_repo.session.begin_nested():

            approval = await self._get_pending(approval_id, for_update=True)

            AccessControl.check_not_creator(actor, approval.created_by_id)

            if approval.status != ApprovalStatus.PENDING:
                raise BadRequest("Already decided")

            approval.status = ApprovalStatus.APPROVED
            approval.approved_by_id = actor.id
            approval.decided_at = utc_now()

            await self.approval_repo.flush()

            await self._execute_approved_action(approval, actor)

            approval.executed = True

            if comment:
                payload = dict(approval.payload or {})
                payload["approval_comment"] = comment.strip()
                approval.payload = payload

            await self.approval_repo.flush()

        # Create Notification
        payload = NotificationBuilder.approval_approved(
            user_id=approval.created_by_id
        )
        await self.notification_dispatcher.dispatch(payload)

        return ApprovalSchema.model_validate(approval, from_attributes=True)

    async def reject(
        self, approval_id: UUID, actor: CurrentUserSchema, comment: str | None = None
    ) -> ApprovalSchema:
        check_permissions(actor, Permissions.APPROVALS_REJECT)

        async with self.approval_repo.session.begin_nested():

            approval = await self._get_pending(approval_id, for_update=True)

            AccessControl.check_not_creator(actor, approval.created_by_id)

            approval.status = ApprovalStatus.REJECTED
            approval.executed = True
            approval.approved_by_id = actor.id
            approval.decided_at = utc_now()

            if comment:
                payload = dict(approval.payload or {})
                payload["rejection_comment"] = comment.strip()
                approval.payload = payload

            await self.approval_repo.flush()

        # Create notification
        payload = NotificationBuilder.approval_rejected(
            user_id=approval.created_by_id
        )
        await self.notification_dispatcher.dispatch(payload)

        return ApprovalSchema.model_validate(approval, from_attributes=True)

    async def _get_pending(
        self, approval_id: UUID, for_update: bool = False
    ) -> ApprovalRequest:

        approval = await (
            self.approval_repo.get_by_id_for_update(approval_id)
            if for_update
            else self.approval_repo.get_by_id(approval_id)
        )

        if not approval:
            raise NotFound("Approval not found")

        if approval.executed:
            raise BadRequest("Already executed")

        if approval.status != ApprovalStatus.PENDING:
            raise BadRequest("Already decided")

        return approval

    def _validate_request(self, data: ApprovalCreate) -> dict:

        supported = {
            ("asset_assignment", "assign"),  # 🔥 ДОБАВИЛИ
            ("asset_transfer", "create_transfer"),
            ("asset_archive", "archive"),
            ("asset_delete", "delete"),
            ("repair", "complete_repair"),
        }

        key = (data.entity_type.strip(), data.action.strip())

        if key not in supported:
            raise BadRequest("Unsupported approval request")

        try:
            if key == ("asset_assignment", "assign"):
                return data.payload

            if key == ("asset_transfer", "create_transfer"):
                return jsonable_encoder(
                    AssetTransferCreate(**data.payload).model_dump(exclude_none=True)
                )

            if key == ("asset_archive", "archive"):
                return jsonable_encoder(
                    AssetArchiveApprovalPayload(**data.payload).model_dump(exclude_none=True)
                )

            if key == ("asset_delete", "delete"):
                return jsonable_encoder(
                    AssetDeleteApprovalPayload(**data.payload).model_dump(exclude_none=True)
                )

            if key == ("repair", "complete_repair"):
                return jsonable_encoder(
                    RepairCompleteApprovalPayload(**data.payload).model_dump(exclude_none=True)
                )

        except Exception as exc:
            raise BadRequest(f"Invalid payload: {exc}") from exc

        raise BadRequest("Unsupported approval request")

    async def _execute_approved_action(
        self, approval: ApprovalRequest, actor: CurrentUserSchema
    ) -> None:

        payload = dict(approval.payload or {})

        if approval.entity_type == "asset_assignment":
            user_id = payload.get("user_id")
            if not user_id:
                raise BadRequest("user_id required")

            await self.asset_assignment_service.assign_asset(
                approval.entity_id,
                UUID(str(user_id)),
                actor,
            )
            return

        if approval.entity_type == "asset_transfer":
            await self.transfer_service.create_transfer(
                approval.entity_id,
                AssetTransferCreate(**payload),
                actor,
            )
            return

        if approval.entity_type == "asset_archive":
            await self.asset_service.change_status(
                approval.entity_id,
                AssetStatusChangeRequest(status=AssetStatus.ARCHIVED),
                actor,
            )
            return

        if approval.entity_type == "asset_delete":
            await self.asset_service.delete(approval.entity_id, actor)
            return

        if approval.entity_type == "repair":
            repair_id = UUID(str(payload["repair_id"]))
            payload.pop("repair_id")

            await self.repair_service.complete_repair(
                approval.entity_id,
                repair_id,
                RepairCompleteRequest(**payload),
                actor,
            )
            return

        raise BadRequest("Unsupported execution")
