"""Tests for AssetMaintenance API endpoints."""

from datetime import date, timedelta
from uuid import uuid4

import pytest

pytestmark = pytest.mark.anyio


def _auth(token: str) -> dict[str, str]:
    """Helper to create auth headers."""
    return {"Authorization": f"Bearer {token}", "Host": "localhost"}


async def _create_maintenance(client, asset_id: uuid4, token: str, **kwargs) -> dict:
    """Helper to create a maintenance record."""
    payload = {
        "maintenance_type": kwargs.get("maintenance_type", "Routine check"),
        "performed_at": kwargs.get("performed_at", str(date.today())),
        "performed_by_id": kwargs.get("performed_by_id"),
        "issues_found": kwargs.get("issues_found"),
        "notes": kwargs.get("notes"),
    }
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}

    response = await client.post(
        f"/api/v1/assets/{asset_id}/maintenances/",
        headers=_auth(token),
        json=payload,
    )
    assert response.status_code == 200, f"Failed: {response.text}"
    return response.json()


class TestAssetMaintenanceEndpoints:
    """Test suite for AssetMaintenance CRUD operations."""

    async def test_create_maintenance_success(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        analytics_users,
    ):
        """Test creating a maintenance record."""
        asset_id = analytics_seed["asset_primary"].id
        user_id = analytics_users["admin"].id

        created = await _create_maintenance(
            client,
            asset_id,
            analytics_tokens["superadmin"],
            maintenance_type="Monthly inspection",
            performed_by_id=str(user_id),
            issues_found="No issues found",
            notes="Routine monthly check completed",
        )

        assert created["maintenance_type"] == "Monthly inspection"
        assert "id" in created
        assert created["asset_id"] == str(asset_id)
        assert created["performed_by_id"] == str(user_id)

    async def test_create_maintenance_unauthorized(
        self,
        client,
        analytics_seed,
        analytics_users,
    ):
        """Test creating maintenance without auth token."""
        asset_id = analytics_seed["asset_primary"].id
        user_id = analytics_users["admin"].id

        response = await client.post(
            f"/api/v1/assets/{asset_id}/maintenances/",
            json={
                "maintenance_type": "Test",
                "performed_at": str(date.today()),
                "performed_by_id": str(user_id),
            },
        )
        # Project returns 400 for auth errors in some cases
        assert response.status_code in (400, 401)

    async def test_create_maintenance_invalid_asset(
        self,
        client,
        analytics_tokens,
        analytics_users,
    ):
        """Test creating maintenance for non-existent asset."""
        fake_asset_id = uuid4()
        user_id = analytics_users["admin"].id

        response = await client.post(
            f"/api/v1/assets/{fake_asset_id}/maintenances/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "maintenance_type": "Test",
                "performed_at": str(date.today()),
                "performed_by_id": str(user_id),
            },
        )
        assert response.status_code == 404

    async def test_create_maintenance_missing_required_fields(
        self,
        client,
        analytics_tokens,
        analytics_seed,
    ):
        """Test creating maintenance with missing required fields."""
        asset_id = analytics_seed["asset_primary"].id

        # Missing performed_by_id
        response = await client.post(
            f"/api/v1/assets/{asset_id}/maintenances/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "maintenance_type": "Test",
                "performed_at": str(date.today()),
            },
        )
        assert response.status_code == 400  # Project maps validation errors to 400

    async def test_list_maintenances(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        test_maintenance,
    ):
        """Test listing maintenance records for an asset."""
        asset_id = analytics_seed["asset_primary"].id

        response = await client.get(
            f"/api/v1/assets/{asset_id}/maintenances/",
            headers=_auth(analytics_tokens["superadmin"]),
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Check our test maintenance is in the list
        maintenance_ids = [item["id"] for item in data]
        assert str(test_maintenance.id) in maintenance_ids

    async def test_list_maintenances_empty(
        self,
        client,
        analytics_tokens,
        analytics_seed,
    ):
        """Test listing maintenances for asset with no records."""
        # Use tertiary asset which has no maintenances
        asset_id = analytics_seed["asset_tertiary"].id

        response = await client.get(
            f"/api/v1/assets/{asset_id}/maintenances/",
            headers=_auth(analytics_tokens["superadmin"]),
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_update_maintenance(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        test_maintenance,
    ):
        """Test updating a maintenance record."""
        asset_id = analytics_seed["asset_primary"].id
        maintenance_id = test_maintenance.id

        response = await client.patch(
            f"/api/v1/assets/{asset_id}/maintenances/{maintenance_id}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "notes": "Updated notes",
                "issues_found": "Updated issues",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Updated notes"
        assert data["issues_found"] == "Updated issues"
        assert data["id"] == str(maintenance_id)

    async def test_update_maintenance_not_found(
        self,
        client,
        analytics_tokens,
        analytics_seed,
    ):
        """Test updating non-existent maintenance."""
        asset_id = analytics_seed["asset_primary"].id
        fake_id = uuid4()

        response = await client.patch(
            f"/api/v1/assets/{asset_id}/maintenances/{fake_id}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"notes": "Test"},
        )

        assert response.status_code == 404

    async def test_delete_maintenance(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        test_maintenance,
    ):
        """Test deleting a maintenance record."""
        asset_id = analytics_seed["asset_primary"].id
        maintenance_id = test_maintenance.id

        # Delete
        response = await client.delete(
            f"/api/v1/assets/{asset_id}/maintenances/{maintenance_id}",
            headers=_auth(analytics_tokens["superadmin"]),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "deleted"

        # Verify deletion - list should not contain deleted maintenance
        list_response = await client.get(
            f"/api/v1/assets/{asset_id}/maintenances/",
            headers=_auth(analytics_tokens["superadmin"]),
        )
        items = list_response.json()
        assert not any(item["id"] == str(maintenance_id) for item in items)

    async def test_delete_maintenance_not_found(
        self,
        client,
        analytics_tokens,
        analytics_seed,
    ):
        """Test deleting non-existent maintenance."""
        asset_id = analytics_seed["asset_primary"].id
        fake_id = uuid4()

        response = await client.delete(
            f"/api/v1/assets/{asset_id}/maintenances/{fake_id}",
            headers=_auth(analytics_tokens["superadmin"]),
        )

        assert response.status_code == 404

    async def test_create_maintenance_invalid_date(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        analytics_users,
    ):
        """Test creating maintenance with invalid date format."""
        asset_id = analytics_seed["asset_primary"].id
        user_id = analytics_users["admin"].id

        response = await client.post(
            f"/api/v1/assets/{asset_id}/maintenances/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "maintenance_type": "Test",
                "performed_at": "invalid-date",
                "performed_by_id": str(user_id),
            },
        )

        assert response.status_code == 400  # Project maps validation errors to 400

    async def test_create_maintenance_empty_type(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        analytics_users,
    ):
        """Test creating maintenance with empty maintenance type."""
        asset_id = analytics_seed["asset_primary"].id
        user_id = analytics_users["admin"].id

        response = await client.post(
            f"/api/v1/assets/{asset_id}/maintenances/",
            headers=_auth(analytics_tokens["superadmin"]),
            json={
                "maintenance_type": "",
                "performed_at": str(date.today()),
                "performed_by_id": str(user_id),
            },
        )

        assert response.status_code == 400  # Project maps validation errors to 400

    async def test_create_maintenance_past_date(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        analytics_users,
    ):
        """Test creating maintenance with past date (should be allowed)."""
        asset_id = analytics_seed["asset_primary"].id
        user_id = analytics_users["admin"].id
        past_date = str(date.today() - timedelta(days=30))

        created = await _create_maintenance(
            client,
            asset_id,
            analytics_tokens["superadmin"],
            maintenance_type="Past maintenance",
            performed_at=past_date,
            performed_by_id=str(user_id),
        )

        assert created["maintenance_type"] == "Past maintenance"
        assert created["performed_at"] == past_date

    async def test_update_maintenance_partial(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        test_maintenance,
    ):
        """Test partial update of maintenance record."""
        asset_id = analytics_seed["asset_primary"].id
        maintenance_id = test_maintenance.id

        # Update only notes
        response = await client.patch(
            f"/api/v1/assets/{asset_id}/maintenances/{maintenance_id}",
            headers=_auth(analytics_tokens["superadmin"]),
            json={"notes": "Only notes updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Only notes updated"
        # Other fields should remain unchanged
        assert data["maintenance_type"] == test_maintenance.maintenance_type

    async def test_list_maintenances_unauthorized(
        self,
        client,
        analytics_seed,
    ):
        """Test listing maintenances without auth."""
        asset_id = analytics_seed["asset_primary"].id

        response = await client.get(
            f"/api/v1/assets/{asset_id}/maintenances/",
        )

        assert response.status_code in (400, 401)

    async def test_create_maintenance_different_assets(
        self,
        client,
        analytics_tokens,
        analytics_seed,
        analytics_users,
    ):
        """Test creating maintenances for multiple assets."""
        user_id = analytics_users["admin"].id

        # Create for primary asset
        primary_maintenance = await _create_maintenance(
            client,
            analytics_seed["asset_primary"].id,
            analytics_tokens["superadmin"],
            maintenance_type="Primary check",
            performed_by_id=str(user_id),
        )

        # Create for secondary asset
        secondary_maintenance = await _create_maintenance(
            client,
            analytics_seed["asset_secondary"].id,
            analytics_tokens["superadmin"],
            maintenance_type="Secondary check",
            performed_by_id=str(user_id),
        )

        assert primary_maintenance["maintenance_type"] == "Primary check"
        assert secondary_maintenance["maintenance_type"] == "Secondary check"

        # Verify they are on different assets
        assert primary_maintenance["asset_id"] != secondary_maintenance["asset_id"]
