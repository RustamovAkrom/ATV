# src/services/approvals/handlers/__init__.py
from typing import Dict, Tuple, Type

from services.approvals.handlers.asset_handlers import (
    AssetArchiveHandler,
    AssetAssignmentHandler,
    AssetDeleteHandler,
    AssetTransferHandler,
)
from services.approvals.handlers.base import BaseApprovalHandler
from services.approvals.handlers.repair_handlers import RepairCompleteHandler
from services.approvals.handlers.warehouse_handlers import WarehouseMoveHandler


class ApprovalHandlerRegistry:
    """Регистр всех обработчиков approval запросов"""

    _handlers: dict[tuple[str, str], BaseApprovalHandler] = {}

    @classmethod
    def register(cls, handler: BaseApprovalHandler):
        """Регистрация обработчика"""
        key = (handler.entity_type.lower(), handler.action.lower())
        cls._handlers[key] = handler

    @classmethod
    def get(cls, entity_type: str, action: str) -> BaseApprovalHandler | None:
        """Получение обработчика по типу и действию"""
        return cls._handlers.get((entity_type.lower(), action.lower()))

    @classmethod
    def get_all(cls) -> dict[tuple[str, str], BaseApprovalHandler]:
        """Получение всех обработчиков"""
        return cls._handlers.copy()

    @classmethod
    def get_supported_keys(cls) -> set:
        """Получение всех поддерживаемых ключей"""
        return set(cls._handlers.keys())


def register_all_handlers() -> dict[tuple[str, str], BaseApprovalHandler]:
    """Регистрация всех обработчиков"""
    handlers = [
        AssetAssignmentHandler(),
        AssetTransferHandler(),
        AssetArchiveHandler(),
        AssetDeleteHandler(),
        RepairCompleteHandler(),
        WarehouseMoveHandler(),
    ]

    for handler in handlers:
        ApprovalHandlerRegistry.register(handler)

    return ApprovalHandlerRegistry.get_all()
