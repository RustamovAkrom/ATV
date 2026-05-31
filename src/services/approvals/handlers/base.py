# src/services/approvals/handlers/base.py
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from schemas.auth.auth import CurrentUserSchema


class BaseApprovalHandler(ABC):
    """Base class for approval handlers. Each handler should implement
    the execute method to perform the action when approval is granted."""

    @property
    @abstractmethod
    def entity_type(self) -> str: ...

    @property
    @abstractmethod
    def action(self) -> str: ...

    @property
    @abstractmethod
    def payload_schema(self) -> type[BaseModel]: ...

    @abstractmethod
    async def execute(
        self, entity_id: UUID, payload: dict[str, Any], actor: CurrentUserSchema
    ) -> Any: ...

    def validate_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self.payload_schema(**payload)
        return validated.model_dump(exclude_none=True)

    @abstractmethod
    def set_services(self, **services: Any) -> None: ...
