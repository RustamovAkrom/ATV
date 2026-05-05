from __future__ import annotations

from core.notifications.dispatcher import NotificationDispatcher
from sqlalchemy import select

from db.models.enums import UserRole, UserStatus
from db.models.users.permission import Role
from db.models.users.user import User
from repositories.analytics.alert_analytics_repo import AlertAnalyticsRepository
from services.analytics.alert_analytics_service import AlertAnalyticsService


class AnalyticsAlertService:
    def __init__(
        self,
        analytics_alerts: AlertAnalyticsService,
        alert_repo: AlertAnalyticsRepository,
        dispatcher: NotificationDispatcher,
    ):
        self.analytics_alerts = analytics_alerts
        self.alert_repo = alert_repo
        self.dispatcher = dispatcher

    async def collect(self):
        return await self.analytics_alerts.get_alerts()

    async def dispatch(self) -> int:
        alerts = await self.collect()
        if not alerts:
            return 0

        recipients = await self.alert_repo.session.execute(
            select(User.id)
            .join(Role, Role.id == User.role_id)
            .where(
                User.status == UserStatus.ACTIVE.value,
                Role.code.in_(
                    [
                        UserRole.SUPERADMIN.value,
                        UserRole.ADMIN.value,
                        UserRole.REGION_MANAGER.value,
                    ]
                ),
            )
        )
        user_ids = [str(user_id) for user_id in recipients.scalars().all()]
        for user_id in user_ids:
            for alert in alerts:
                await self.dispatcher.dispatch(
                    {
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
                    }
                )
        return len(alerts) * len(user_ids)
