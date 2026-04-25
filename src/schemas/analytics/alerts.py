from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class AlertType(StrEnum):
    STUCK_TRANSFER = "stuck_transfer"
    EXCESSIVE_REPAIRS = "excessive_repairs"
    INACTIVE_ASSET = "inactive_asset"
    OVERLOADED_USER = "overloaded_user"


class AlertSeverity(StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"


class AlertOut(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    entity_id: UUID
    entity_name: str
    message: str
    metric_value: float
    threshold: float
    detected_at: datetime
