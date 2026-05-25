import builtins
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, select

from core.events.approval_events import ApprovalEventService
from core.exceptions.errors import BadRequest, NotFound
from core.security.access_control import AccessControl
from core.security.rbac.guards import check_permissions
from core.security.rbac.permissions import Permissions
from db.models.approvals.approval_request import ApprovalRequest
from db.models.assets.asset import Asset
from db.models.enums import ApprovalStatus, AssetStatus, UserStatus
from db.models.users.permission import Role
from db.models.users.user import User
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
from schemas.assets.warehouses import WarehouseMoveRequest
from schemas.auth.auth import CurrentUserSchema
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from services.assets.asset_assignment_service import AssetAssignmentService
from services.assets.asset_service import AssetService
from services.assets.asset_transfer_service import AssetTransferService
from services.assets.repair_service import RepairService
from services.assets.warehouse_service import WarehouseService
from utils.helpers import utc_now


class ApprovalService:
    def __init__(
        self,
        approval_repo: ApprovalRepository,
        asset_service: AssetService,
        transfer_service: AssetTransferService,
        repair_service: RepairService,
        asset_assignment_service: AssetAssignmentService,
        warehouse_service: WarehouseService,
        approval_events: ApprovalEventService,
    ):
        self.approval_repo = approval_repo
        self.asset_service = asset_service
        self.transfer_service = transfer_service
        self.repair_service = repair_service
        self.asset_assignment_service = asset_assignment_service
        self.warehouse_service = warehouse_service
        self.approval_events = approval_events

    async def list(
        self,
        status: ApprovalStatus | None,
        pagination: PaginationParamsSchema,
    ):
        items, total = await self.approval_repo.list(status, pagination)

        return PageOutSchema(
            items=[
                ApprovalSchema.model_validate(i, from_attributes=True) for i in items
            ],
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def create(
        self, data: ApprovalCreate, actor: CurrentUserSchema
    ) -> ApprovalSchema:
        check_permissions(actor, Permissions.APPROVALS_CREATE)

        validated_payload = self._validate_request(data)

        asset = await self.asset_service._get_asset(data.entity_id)
        if not asset:
            raise NotFound("Asset not found")

        if (
            data.entity_type.strip().lower() == "asset_transfer"
            and data.action.strip().lower() == "create_transfer"
            and asset.is_transfer_locked
        ):
            raise BadRequest("Asset transfer is locked")

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

        approvers = await self._get_approvers(asset, requester_id=actor.id)

        await self.approval_events.requested(
            approval_id=approval.id,
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            action=approval.action,
            requester_id=actor.id,
            approver_ids=approvers,
        )

        return ApprovalSchema.model_validate(approval, from_attributes=True)

    async def approve(
        self, approval_id: UUID, actor: CurrentUserSchema, comment: str | None = None
    ) -> ApprovalSchema:
        check_permissions(actor, Permissions.APPROVALS_APPROVE)

        async with self.approval_repo.session.begin_nested():
            approval = await self._get_pending(approval_id, for_update=True)

            AccessControl.check_not_creator(actor, approval.created_by_id)

            asset = await self.asset_service._get_asset(approval.entity_id)

            AccessControl.check_region_access(actor, asset.region_id)
            AccessControl.check_service_access(actor, asset.service_id)

            approval.status = ApprovalStatus.APPROVED
            approval.approved_by_id = actor.id
            approval.decided_at = utc_now()

            await self.approval_repo.flush()

            await self._execute_approved_action(approval, actor)

            approval.executed = True

            await self.approval_repo.flush()

            if comment:
                payload = dict(approval.payload or {})
                payload["approval_comment"] = comment.strip()
                approval.payload = payload
            await self.approval_repo.flush()

        await self.approval_events.approved(
            approval_id=approval.id,
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            action=approval.action,
            requester_id=approval.created_by_id,
            approver_id=actor.id,
        )

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

        await self.approval_events.rejected(
            approval_id=approval.id,
            entity_type=approval.entity_type,
            entity_id=approval.entity_id,
            action=approval.action,
            requester_id=approval.created_by_id,
            approver_id=actor.id,
            reason=comment,
        )

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
        # TODO: Takomilashtirish kerak pydantic ishlatish kerak bazoviy supported methodlarni yozib qoyish kerak yana qoshimcha methodlarni qoshish imkoniyatiniyam kirgizish kerak avtomatik bolishi shart hamasi qulay va tushinarli sodda bolishi kerak
        supported = {
            ("asset_assignment", "assign"),
            ("asset_transfer", "create_transfer"),
            ("asset_archive", "archive"),
            ("asset_delete", "delete"),
            ("repair", "complete_repair"),
            ("asset", "move_to_warehouse"),
        }

        entity_type = data.entity_type.strip().lower()
        action = data.action.strip().lower()

        key = (entity_type, action)

        if key not in supported:
            raise BadRequest("Unsupported approval request")

        try:
            if key == ("asset_assignment", "assign"):
                user_id = data.payload.get("user_id")
                if not user_id:
                    raise BadRequest("user_id required in payload")
                return {"user_id": str(user_id)}

            if key == ("asset_transfer", "create_transfer"):
                return jsonable_encoder(
                    AssetTransferCreate(**data.payload).model_dump(exclude_none=True)
                )

            if key == ("asset_archive", "archive"):
                return jsonable_encoder(
                    AssetArchiveApprovalPayload(**data.payload).model_dump(
                        exclude_none=True
                    )
                )

            if key == ("asset_delete", "delete"):
                return jsonable_encoder(
                    AssetDeleteApprovalPayload(**data.payload).model_dump(
                        exclude_none=True
                    )
                )

            if key == ("repair", "complete_repair"):
                return jsonable_encoder(
                    RepairCompleteApprovalPayload(**data.payload).model_dump(
                        exclude_none=True
                    )
                )

            if key == ("asset", "move_to_warehouse"):
                return jsonable_encoder(
                    WarehouseMoveRequest(**data.payload).model_dump(exclude_none=True)
                )

        except Exception as exc:
            raise BadRequest(f"Invalid payload: {exc}") from exc

        raise BadRequest("Unsupported approval request")

    async def _execute_approved_action(
        self, approval: ApprovalRequest, actor: CurrentUserSchema
    ) -> None:

        payload = dict(approval.payload or {})

        if not isinstance(payload, dict):
            raise BadRequest("Invalid payload format")

        # asset_assignment
        if approval.entity_type == "asset_assignment":
            user_id = payload.get("user_id")
            if not user_id:
                raise BadRequest("user_id required")

            asset = await self.asset_service._get_asset(approval.entity_id)
            if asset.owner_id is not None:
                await self.asset_assignment_service.reassign_asset(
                    approval.entity_id,
                    UUID(str(user_id)),
                    actor,
                )
            else:
                await self.asset_assignment_service.assign_asset(
                    approval.entity_id,
                    UUID(str(user_id)),
                    actor,
                )
            await self.approval_events.executed(
                approval_id=approval.id,
                entity_type=approval.entity_type,
                entity_id=approval.entity_id,
                action=approval.action,
                requester_id=approval.created_by_id,
            )
            return

        # asset_transfer
        if approval.entity_type == "asset_transfer":
            transfer = await self.transfer_service.create_transfer(
                approval.entity_id,
                AssetTransferCreate(**payload),
                actor,
                requested_by_id=approval.created_by_id,
            )
            await self.transfer_service.approve_transfer(
                approval.entity_id,
                transfer.id,
                actor,
                comment=payload.get("comment"),
            )
            await self.approval_events.executed(
                approval_id=approval.id,
                entity_type=approval.entity_type,
                entity_id=approval.entity_id,
                action=approval.action,
                requester_id=approval.created_by_id,
            )
            return

        # asset_archive
        if approval.entity_type == "asset_archive":
            status_request = AssetStatusChangeRequest(status=AssetStatus.ARCHIVED)
            await self.asset_service.change_status(
                approval.entity_id,
                status_request,
                actor,
            )
            await self.approval_events.executed(
                approval_id=approval.id,
                entity_type=approval.entity_type,
                entity_id=approval.entity_id,
                action=approval.action,
                requester_id=approval.created_by_id,
            )
            return

        # asset_delete
        if approval.entity_type == "asset_delete":
            await self.asset_service.delete(approval.entity_id, actor)
            await self.approval_events.executed(
                approval_id=approval.id,
                entity_type=approval.entity_type,
                entity_id=approval.entity_id,
                action=approval.action,
                requester_id=approval.created_by_id,
            )
            return

        # repair
        if approval.entity_type == "repair":
            repair_id = UUID(str(payload["repair_id"]))
            payload.pop("repair_id")

            await self.repair_service.complete_repair(
                approval.entity_id,
                repair_id,
                RepairCompleteRequest(**payload),
                actor,
            )
            await self.approval_events.executed(
                approval_id=approval.id,
                entity_type=approval.entity_type,
                entity_id=approval.entity_id,
                action=approval.action,
                requester_id=approval.created_by_id,
            )
            return

        # asset -> move_to_warehouse
        if approval.entity_type == "asset":
            if approval.action == "move_to_warehouse":
                await self.warehouse_service.move_asset_to_warehouse(
                    approval.entity_id,
                    WarehouseMoveRequest(**payload),
                    actor,
                )
                await self.approval_events.executed(
                    approval_id=approval.id,
                    entity_type=approval.entity_type,
                    entity_id=approval.entity_id,
                    action=approval.action,
                    requester_id=approval.created_by_id,
                )
                return

        raise BadRequest("Unsupported execution")

    async def _get_approvers(
        self, asset: Asset, requester_id: UUID
    ) -> builtins.list[UUID]:
        result = await self.approval_repo.session.execute(
            select(User)
            .join(Role, User.role_id == Role.id)
            .where(
                User.status == UserStatus.ACTIVE.value,
                User.id != requester_id,
                or_(
                    User.assigned_region_id.is_(None),
                    User.assigned_region_id == asset.region_id,
                ),
                or_(
                    User.assigned_service_id.is_(None),
                    User.assigned_service_id == asset.service_id,
                ),
            )
        )
        users = result.scalars().all()
        return [
            user.id
            for user in users
            if user.role
            and any(
                str(getattr(p, "slug", "")).lower() == Permissions.APPROVALS_APPROVE
                for p in (user.role.permissions or [])
            )
        ]
