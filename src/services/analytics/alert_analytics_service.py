from datetime import timedelta

from core.config import get_settings
from core.notifications.dispatcher import NotificationDispatcher
from db.models.enums import UserRole, UserStatus
from db.models.users.permission import Role
from db.models.users.user import User
from repositories.analytics.alert_analytics_repo import AlertAnalyticsRepository
from schemas.analytics.alerts import AlertOut, AlertSeverity, AlertType
from services.analytics.base_analytics_service import BaseAnalyticsService
from sqlalchemy import select
from utils.helpers import utc_now

settings = get_settings()


class AlertAnalyticsService(BaseAnalyticsService):
    def __init__(self, repo: AlertAnalyticsRepository, dispatcher: NotificationDispatcher | None = None):
        self.repo = repo
        self.dispatcher = dispatcher

    async def get_alerts(
        self,
        transfer_days: int | None = None,
        repair_days: int | None = None,
        repair_threshold: int | None = None,
        inactive_days: int | None = None,
        assignment_threshold: int | None = None,
    ) -> list[AlertOut]:
        transfer_days = transfer_days or settings.ALERT_TRANSFER_DAYS_LIMIT
        repair_days = repair_days or settings.ALERT_REPAIR_LOOKBACK_DAYS
        repair_threshold = repair_threshold or settings.ALERT_REPAIR_THRESHOLD
        inactive_days = inactive_days or settings.ALERT_INACTIVE_ASSET_DAYS
        assignment_threshold = assignment_threshold or settings.ALERT_OVERLOADED_USER_THRESHOLD

        now = utc_now()
        transfer_cutoff = now - timedelta(days=transfer_days)
        repair_cutoff = now - timedelta(days=repair_days)
        inactive_cutoff = now - timedelta(days=inactive_days)

        stuck_transfers = await self.repo.stuck_transfers(transfer_cutoff)
        excessive_repairs = await self.repo.excessive_repairs(repair_cutoff, repair_threshold)
        inactive_assets = await self.repo.inactive_assets(inactive_cutoff)
        overloaded_users = await self.repo.overloaded_users(assignment_threshold)

        alerts: list[AlertOut] = []

        for row in stuck_transfers:
            alerts.append(AlertOut.model_construct(
                alert_type=AlertType.STUCK_TRANSFER,
                severity=AlertSeverity.CRITICAL,
                entity_id=row.id,
                entity_name=row.name,
                message=f"Transfer pending longer than {transfer_days} days",
                metric_value=float((now - row.created_at).days),
                threshold=float(transfer_days),
                detected_at=now,
            ))

        for row in excessive_repairs:
            alerts.append(AlertOut.model_construct(
                alert_type=AlertType.EXCESSIVE_REPAIRS,
                severity=(
                    AlertSeverity.CRITICAL
                    if int(row.repair_count or 0) > repair_threshold * settings.ALERT_REPAIR_THRESHOLD_MULTIPLIER
                    else AlertSeverity.WARNING
                ),
                entity_id=row.id,
                entity_name=row.name,
                message=f"Asset exceeded {repair_threshold} repairs in the review window",
                metric_value=float(row.repair_count) if row.repair_count else 0,
                threshold=float(repair_threshold),
                detected_at=now,
            ))

        for row in inactive_assets:
            alerts.append(AlertOut.model_construct(
                alert_type=AlertType.INACTIVE_ASSET,
                severity=AlertSeverity.WARNING,
                entity_id=row.id,
                entity_name=row.name,
                message=f"No recent activity for more than {inactive_days} days",
                metric_value=float((now - row.updated_at).days),
                threshold=float(inactive_days),
                detected_at=now,
            ))

        for row in overloaded_users:
            alerts.append(AlertOut.model_construct(
                alert_type=AlertType.OVERLOADED_USER,
                severity=(
                    AlertSeverity.CRITICAL
                    if int(row.active_assignments or 0) > assignment_threshold * settings.ALERT_REPAIR_THRESHOLD_MULTIPLIER
                    else AlertSeverity.WARNING
                ),
                entity_id=row.id,
                entity_name=row.full_name,
                message=f"User holds more than {assignment_threshold} active assignments",
                metric_value=float(row.active_assignments) if row.active_assignments else 0,
                threshold=float(assignment_threshold),
                detected_at=now,
            ))

        return alerts

    async def dispatch_alerts(self) -> int:
        if not self.dispatcher:
            return 0

        alerts = await self.get_alerts()
        if not alerts:
            return 0

        recipients = await self.repo.session.execute(
            select(User.id)
            .join(Role, Role.id == User.role_id)
            .where(
                User.status == UserStatus.ACTIVE.value,
                Role.slug.in_([UserRole.SUPERADMIN.value, UserRole.ADMIN.value, UserRole.REGION_MANAGER.value]),
            )
        )
        user_ids = [str(user_id) for user_id in recipients.scalars().all()]

        for user_id in user_ids:
            for alert in alerts:
                await self.dispatcher.dispatch({
                    "user_id": user_id,
                    "type": "analytics.alert",
                    "title": "Analytics Alert",
                    "message": alert.message,
                    "data": {
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "entity_id": str(alert.entity_id),
                        "metric_value": alert.metric_value,
                        "threshold": alert.threshold,
                    },
                })

        return len(alerts) * len(user_ids)

