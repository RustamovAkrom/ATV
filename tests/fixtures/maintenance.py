"""Fixtures for AssetMaintenance tests."""
import pytest

from tests.factories.maintenance import create_maintenance


@pytest.fixture
async def test_maintenance(dbsession, analytics_seed, analytics_users):
    """Create a test maintenance record on the primary asset."""
    maintenance = await create_maintenance(
        dbsession,
        asset=analytics_seed["asset_primary"],
        performed_by=analytics_users["admin"],
        maintenance_type="Monthly inspection",
        issues_found="No issues",
        notes="Routine check",
    )
    return maintenance
