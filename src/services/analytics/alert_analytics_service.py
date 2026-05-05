from datetime import timedelta

from core.config import get_settings
from repositories.analytics.alert_analytics_repo import AlertAnalyticsRepository
from schemas.analytics.alerts import AlertOut, AlertSeverity, AlertType
from utils.helpers import utc_now

settings = get_settings()


class AlertAnalyticsService:
    def __init__(self, repo: AlertAnalyticsRepository):
        self.repo = repo

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
        assignment_threshold = (
            assignment_threshold or settings.ALERT_OVERLOADED_USER_THRESHOLD
        )
        now = utc_now()
        transfer_cutoff = now - timedelta(days=transfer_days)
        repair_cutoff = now - timedelta(days=repair_days)
        inactive_cutoff = now - timedelta(days=inactive_days)

        stuck_transfers = await self.repo.stuck_transfers(transfer_cutoff)
        excessive_repairs = await self.repo.excessive_repairs(
            repair_cutoff, repair_threshold
        )
        inactive_assets = await self.repo.inactive_assets(inactive_cutoff)
        overloaded_users = await self.repo.overloaded_users(assignment_threshold)

        alerts = [
            AlertOut(
                alert_type=AlertType.STUCK_TRANSFER,
                severity=AlertSeverity.CRITICAL,
                entity_id=row.id,
                entity_name=row.name,
                message=f"Transfer pending longer than {transfer_days} days",
                metric_value=float((now - row.created_at).days),
                threshold=float(transfer_days),
                detected_at=now,
            )
            for row in stuck_transfers
        ]
        alerts.extend(
            AlertOut(
                alert_type=AlertType.EXCESSIVE_REPAIRS,
                # Use settings-driven multipliers so the alert policy can
                # change without code edits.
                severity=(
                    AlertSeverity.CRITICAL
                    if row.repair_count
                    > repair_threshold * settings.ALERT_REPAIR_THRESHOLD_MULTIPLIER
                    else AlertSeverity.WARNING
                ),
                entity_id=row.id,
                entity_name=row.name,
                message=(
                    f"Asset exceeded {repair_threshold} repairs in the review window"
                ),
                metric_value=float(row.repair_count),
                threshold=float(repair_threshold),
                detected_at=now,
            )
            for row in excessive_repairs
        )
        alerts.extend(
            AlertOut(
                alert_type=AlertType.INACTIVE_ASSET,
                severity=AlertSeverity.WARNING,
                entity_id=row.id,
                entity_name=row.name,
                message=f"No recent activity for more than {inactive_days} days",
                metric_value=float((now - row.updated_at).days),
                threshold=float(inactive_days),
                detected_at=now,
            )
            for row in inactive_assets
        )
        alerts.extend(
            AlertOut(
                alert_type=AlertType.OVERLOADED_USER,
                severity=(
                    AlertSeverity.CRITICAL
                    if row.active_assignments
                    > assignment_threshold * settings.ALERT_REPAIR_THRESHOLD_MULTIPLIER
                    else AlertSeverity.WARNING
                ),
                entity_id=row.id,
                entity_name=row.full_name,
                message=(
                    f"User holds more than {assignment_threshold} active assignments"
                ),
                metric_value=float(row.active_assignments),
                threshold=float(assignment_threshold),
                detected_at=now,
            )
            for row in overloaded_users
        )
        return alerts
