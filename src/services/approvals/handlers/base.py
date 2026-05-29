# src/services/approvals/handlers/base.py
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from schemas.auth.auth import CurrentUserSchema


class BaseApprovalHandler(ABC):
    """Базовый класс для всех обработчиков approval запросов"""

    @property
    @abstractmethod
    def entity_type(self) -> str:
        """Тип сущности (asset_assignment, repair, asset_transfer и т.д.)"""
        pass

    @property
    @abstractmethod
    def action(self) -> str:
        """Действие (assign, complete_repair, create_transfer и т.д.)"""
        pass

    @property
    @abstractmethod
    def payload_schema(self) -> type[BaseModel]:
        """Pydantic схема для валидации payload"""
        pass

    @abstractmethod
    async def execute(
        self, entity_id: UUID, payload: dict[str, Any], actor: CurrentUserSchema
    ) -> Any:
        """Выполнение действия после одобрения"""
        pass

    def validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Валидация payload с использованием Pydantic схемы"""
        validated = self.payload_schema(**payload)
        return validated.model_dump(exclude_none=True)
