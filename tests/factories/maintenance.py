"""Factories for AssetMaintenance test data."""

from datetime import date

from db.models.assets.asset import Asset
from db.models.assets.asset_maintenance import AssetMaintenance
from db.models.users.user import User


async def create_maintenance(
    dbsession,
    *,
    asset: Asset,
    performed_by: User,
    maintenance_type: str = "Routine check",
    performed_at: date | None = None,
    issues_found: str | None = None,
    notes: str | None = None,
) -> AssetMaintenance:
    """Create an AssetMaintenance record for testing."""
    maintenance = AssetMaintenance(
        asset_id=asset.id,
        maintenance_type=maintenance_type,
        performed_at=performed_at or date.today(),
        issues_found=issues_found,
        performed_by_id=performed_by.id,
        notes=notes,
    )
    dbsession.add(maintenance)
    await dbsession.flush()
    return maintenance
