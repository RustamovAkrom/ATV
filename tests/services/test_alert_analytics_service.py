from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest

from services.analytics.alert_analytics_service import AlertAnalyticsService

pytestmark = pytest.mark.anyio


class _AlertRepo:
    async def stuck_transfers(self, cutoff):
        return [
            SimpleNamespace(
                id=uuid4(), name="TransferAsset", created_at=cutoff - timedelta(days=1)
            )
        ]

    async def excessive_repairs(self, since, threshold):
        return [
            SimpleNamespace(id=uuid4(), name="RepairAsset", repair_count=threshold + 1)
        ]

    async def inactive_assets(self, cutoff):
        return [
            SimpleNamespace(
                id=uuid4(), name="InactiveAsset", updated_at=cutoff - timedelta(days=1)
            )
        ]

    async def overloaded_users(self, threshold):
        return [
            SimpleNamespace(
                id=uuid4(), full_name="Busy User", active_assignments=threshold + 1
            )
        ]


async def test_alert_service_uses_configurable_thresholds():
    service = AlertAnalyticsService(_AlertRepo())

    result = await service.get_alerts(
        transfer_days=2,
        repair_days=30,
        repair_threshold=1,
        inactive_days=10,
        assignment_threshold=1,
    )

    assert {item.alert_type.value for item in result} == {
        "stuck_transfer",
        "excessive_repairs",
        "inactive_asset",
        "overloaded_user",
    }
