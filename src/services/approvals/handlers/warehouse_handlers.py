# src/services/approvals/handlers/warehouse_handlers.py
from typing import Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field

from services.approvals.handlers.base import BaseApprovalHandler
from schemas.auth.auth import CurrentUserSchema
from schemas.assets.warehouses import WarehouseMoveRequest


class WarehouseMovePayload(BaseModel):
    """Payload для перемещения актива на склад"""

    warehouse_id: UUID = Field(..., description="ID склада")

    class Config:
        json_schema_extra = {
            "example": {"warehouse_id": "123e4567-e89b-12d3-a456-426614174000"}
        }


class WarehouseMoveHandler(BaseApprovalHandler):
    """Обработчик approval запроса на перемещение актива на склад"""

    def __init__(self):
        self.warehouse_service = None

    def set_services(self, **services):
        """Внедрение зависимостей"""
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
        self, entity_id: UUID, payload: Dict[str, Any], actor: CurrentUserSchema
    ):
        """
        Выполнение перемещения актива на склад после одобрения

        Args:
            entity_id: ID актива (asset_id)
            payload: Данные запроса (warehouse_id)
            actor: Пользователь, который одобрил запрос
        """
        if not self.warehouse_service:
            raise RuntimeError("WarehouseService not injected")

        # Создаем запрос на перемещение
        move_request = WarehouseMoveRequest(warehouse_id=payload.get("warehouse_id"))

        # Выполняем перемещение
        return await self.warehouse_service.move_asset_to_warehouse(
            asset_id=entity_id, data=move_request, actor=actor
        )
