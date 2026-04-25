import pytest

from repositories.analytics.asset_assignment_analytics_repo import (
    AssetAssignmentAnalyticsRepository,
)
from repositories.analytics.asset_transfer_analytics_repo import (
    AssetTransferAnalyticsRepository,
)
from repositories.analytics.region_analytics_repo import RegionAnalyticsRepository
from schemas.analytics.asset_assignment_analytics import AssetAssignmentFilterInput
from schemas.analytics.asset_transfer_analytics import AssetTransferFilterInput

pytestmark = pytest.mark.anyio


async def test_region_repository_returns_correct_overview(dbsession, analytics_seed):
    repo = RegionAnalyticsRepository(dbsession)

    rows = await repo.list_overview()

    assert len(rows) == 1
    assert rows[0].total_assets == 3
    assert rows[0].repairs_count == 2
    assert rows[0].assignment_load == 3


async def test_assignment_repository_aggregates_and_filters(dbsession, analytics_seed):
    repo = AssetAssignmentAnalyticsRepository(dbsession)

    active_items, active_total = await repo.list_assignments(
        AssetAssignmentFilterInput(status="active"),
        type("Pagination", (), {"limit": 20, "offset": lambda self: 0})(),
    )
    aggregates = await repo.get_aggregates(AssetAssignmentFilterInput())

    assert active_total == 3
    assert len(active_items) == 3
    assert aggregates["total_assignments"] == 4
    assert aggregates["total_active_assignments"] == 3


async def test_transfer_repository_metrics_and_bottlenecks(dbsession, analytics_seed):
    repo = AssetTransferAnalyticsRepository(dbsession)

    aggregates = await repo.get_transfer_aggregates(AssetTransferFilterInput())
    bottlenecks = await repo.get_bottlenecks(critical_days=2, warning_days=1)

    assert aggregates["total_transfers"] == 2
    assert aggregates["pending_transfers"] == 1
    assert aggregates["completed_transfers"] == 1
    assert len(bottlenecks["critical"]) >= 1
