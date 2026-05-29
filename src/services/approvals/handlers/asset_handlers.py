# src/services/approvals/handlers/asset_handlers.py
from typing import Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field

from services.approvals.handlers.base import BaseApprovalHandler
from schemas.auth.auth import CurrentUserSchema
from schemas.assets.asset_transfers import AssetTransferCreate
from schemas.assets.assets import AssetStatusChangeRequest
from db.models.enums import AssetStatus


class AssetAssignmentPayload(BaseModel):
    """Payload для назначения актива"""

    user_id: UUID = Field(..., description="ID пользователя которому назначается актив")

    class Config:
        json_schema_extra = {
            "example": {"user_id": "123e4567-e89b-12d3-a456-426614174000"}
        }


class AssetAssignmentHandler(BaseApprovalHandler):
    def __init__(self):
        self.asset_assignment_service = None
        self.asset_service = None

    def set_services(self, **services):
        self.asset_assignment_service = services.get("asset_assignment_service")
        self.asset_service = services.get("asset_service")

    @property
    def entity_type(self) -> str:
        return "asset_assignment"

    @property
    def action(self) -> str:
        return "assign"

    @property
    def payload_schema(self):
        return AssetAssignmentPayload

    async def execute(
        self, entity_id: UUID, payload: Dict[str, Any], actor: CurrentUserSchema
    ):
        if not self.asset_assignment_service:
            raise RuntimeError("AssetAssignmentService not injected")

        user_id = payload.get("user_id")
        asset = await self.asset_service._get_asset(entity_id)

        if asset.owner_id is not None:
            return await self.asset_assignment_service.reassign_asset(
                entity_id, UUID(str(user_id)), actor
            )
        else:
            return await self.asset_assignment_service.assign_asset(
                entity_id, UUID(str(user_id)), actor
            )


class AssetTransferPayload(BaseModel):
    """Payload для трансфера актива"""

    to_warehouse_id: UUID | None = Field(None, description="ID целевого склада")
    to_service_id: UUID | None = Field(None, description="ID целевой службы")
    comment: str | None = Field(None, description="Комментарий", max_length=255)

    class Config:
        json_schema_extra = {
            "example": {
                "to_warehouse_id": "123e4567-e89b-12d3-a456-426614174000",
                "comment": "Перевод на склад",
            }
        }


class AssetTransferHandler(BaseApprovalHandler):
    def __init__(self):
        self.transfer_service = None

    def set_services(self, **services):
        self.transfer_service = services.get("transfer_service")

    @property
    def entity_type(self) -> str:
        return "asset_transfer"

    @property
    def action(self) -> str:
        return "create_transfer"

    @property
    def payload_schema(self):
        return AssetTransferPayload

    async def execute(
        self, entity_id: UUID, payload: Dict[str, Any], actor: CurrentUserSchema
    ):
        if not self.transfer_service:
            raise RuntimeError("AssetTransferService not injected")

        transfer_create = AssetTransferCreate(**payload)
        transfer = await self.transfer_service.create_transfer(
            entity_id, transfer_create, actor, requested_by_id=actor.id
        )
        await self.transfer_service.approve_transfer(
            entity_id, transfer.id, actor, comment=payload.get("comment")
        )
        return transfer


class AssetArchivePayload(BaseModel):
    """Payload для архивации актива"""

    reason: str | None = Field(None, description="Причина архивации", max_length=500)

    class Config:
        json_schema_extra = {"example": {"reason": "Актив списан"}}


class AssetArchiveHandler(BaseApprovalHandler):
    def __init__(self):
        self.asset_service = None

    def set_services(self, **services):
        self.asset_service = services.get("asset_service")

    @property
    def entity_type(self) -> str:
        return "asset_archive"

    @property
    def action(self) -> str:
        return "archive"

    @property
    def payload_schema(self):
        return AssetArchivePayload

    async def execute(
        self, entity_id: UUID, payload: Dict[str, Any], actor: CurrentUserSchema
    ):
        if not self.asset_service:
            raise RuntimeError("AssetService not injected")

        status_request = AssetStatusChangeRequest(status=AssetStatus.ARCHIVED)
        return await self.asset_service.change_status(entity_id, status_request, actor)


class AssetDeletePayload(BaseModel):
    """Payload для удаления актива"""

    reason: str | None = Field(None, description="Причина удаления", max_length=500)

    class Config:
        json_schema_extra = {"example": {"reason": "Ошибочный актив"}}


class AssetDeleteHandler(BaseApprovalHandler):
    def __init__(self):
        self.asset_service = None

    def set_services(self, **services):
        self.asset_service = services.get("asset_service")

    @property
    def entity_type(self) -> str:
        return "asset_delete"

    @property
    def action(self) -> str:
        return "delete"

    @property
    def payload_schema(self):
        return AssetDeletePayload

    async def execute(
        self, entity_id: UUID, payload: Dict[str, Any], actor: CurrentUserSchema
    ):
        if not self.asset_service:
            raise RuntimeError("AssetService not injected")

        return await self.asset_service.delete(entity_id, actor)
