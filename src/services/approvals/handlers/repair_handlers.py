# src/services/approvals/handlers/repair_handlers.py
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from schemas.assets.repairs import RepairCompleteRequest
from schemas.auth.auth import CurrentUserSchema
from services.approvals.handlers.base import BaseApprovalHandler


class RepairCompleteHandler(BaseApprovalHandler):
    def __init__(self):
        self.repair_service = None

    def set_services(self, **services):
        self.repair_service = services.get("repair_service")

    @property
    def entity_type(self) -> str:
        return "repair"

    @property
    def action(self) -> str:
        return "complete_repair"

    @property
    def payload_schema(self):
        return RepairCompleteRequest

    async def execute(
        self,
        entity_id: UUID,
        payload: dict[str, Any],
        actor: CurrentUserSchema,
    ):
        if not self.repair_service:
            raise RuntimeError("RepairService not injected")

        repair_id = UUID(str(payload.get("repair_id")))
        payload_without_repair_id = {
            k: v for k, v in payload.items() if k != "repair_id"
        }

        return await self.repair_service.complete_repair(
            entity_id,
            repair_id,
            RepairCompleteRequest(**payload_without_repair_id),
            actor,
        )

    def validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Validate payload and ensure repair_id is present"""
        # Ремонт ID должен быть в payload
        repair_id = payload.get("repair_id")
        if not repair_id:
            raise ValueError("repair_id is required in payload")

        # Валидируем остальной payload через RepairCompleteRequest
        validated = RepairCompleteRequest(
            **{k: v for k, v in payload.items() if k != "repair_id"}
        )
        validated_payload = validated.model_dump(exclude_none=True)
        validated_payload["repair_id"] = UUID(str(repair_id))
        return validated_payload


class WarehouseMovePayload(BaseModel):
    """Payload для перемещения на склад"""

    warehouse_id: UUID = Field(..., description="ID склада")

    class Config:
        json_schema_extra = {
            "example": {"warehouse_id": "123e4567-e89b-12d3-a456-426614174000"}
        }


class WarehouseMoveHandler(BaseApprovalHandler):
    def __init__(self):
        self.warehouse_service = None

    def set_services(self, **services):
        self.warehouse_service = services.get("warehouse_service")

    @property
    def entity_type(self) -> str:
        return "asset"

    @property
    def action(self) -> str:
        return "move_to_warehouse"

    @property
    def payload_schema(self):
        return WarehouseMovePayload

    async def execute(
        self,
        entity_id: UUID,
        payload: dict[str, Any],
        actor: CurrentUserSchema,
    ):
        if not self.warehouse_service:
            raise RuntimeError("WarehouseService not injected")

        from schemas.assets.warehouses import WarehouseMoveRequest

        return await self.warehouse_service.move_asset_to_warehouse(
            entity_id, WarehouseMoveRequest(**payload), actor
        )
