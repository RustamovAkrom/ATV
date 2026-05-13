import pytest

pytestmark = pytest.mark.anyio


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_dashboard_overview_returns_stable_payload(
    client, analytics_seed, analytics_tokens
):
    response = await client.get(
        "/analytics/dashboard/overview/",
        headers=_auth(analytics_tokens["superadmin"]),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["period"] == "all_time"
    assert payload["assignment_metrics"]["total_active"] >= 1
    assert payload["transfer_metrics"]["total_pending"] >= 1
    assert payload["asset_history_metrics"]["total_history_entries"] >= 1


async def test_dashboard_overview_requires_auth(client):
    response = await client.get("/analytics/dashboard/overview/")
    assert response.status_code in {401, 403}


async def test_regions_endpoints_return_geo_and_aggregates(
    client, analytics_seed, analytics_tokens
):
    overview = await client.get(
        "/analytics/regions/overview", headers=_auth(analytics_tokens["superadmin"])
    )
    assert overview.status_code == 200
    overview_payload = overview.json()
    assert len(overview_payload) == 1
    assert overview_payload[0]["geojson"]
    assert overview_payload[0]["asset_counts"]["total"] == 3

    region_id = overview_payload[0]["region_id"]
    details = await client.get(
        f"/analytics/regions/{region_id}/details",
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert details.status_code == 200
    details_payload = details.json()
    assert details_payload["services"]
    assert details_payload["top_cost_assets"]

    heatmap = await client.get(
        "/analytics/regions/heatmap", headers=_auth(analytics_tokens["superadmin"])
    )
    assert heatmap.status_code == 200
    assert heatmap.json()[0]["score"] > 0


async def test_assignment_analytics_filters_aggregates_and_timeline(
    client, analytics_seed, analytics_tokens
):
    asset_id = str(analytics_seed["asset_primary"].id)

    listing = await client.get(
        "/analytics/assignments/",
        params={"asset_id": asset_id, "status": "active"},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "active"
    assert "duration_metrics" in body["items"][0]

    aggregates = await client.get(
        "/analytics/assignments/aggregates",
        params={"asset_id": asset_id},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert aggregates.status_code == 200
    assert aggregates.json()["total_assignments"] >= 2

    timeline = await client.get(
        f"/analytics/assignments/asset/{asset_id}/timeline",
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert timeline.status_code == 200
    timeline_payload = timeline.json()
    assert timeline_payload["asset_id"] == asset_id
    assert timeline_payload["total_assignments"] >= 2


async def test_transfer_analytics_list_metrics_and_bottlenecks(
    client, analytics_seed, analytics_tokens
):
    listing = await client.get(
        "/analytics/transfers/", headers=_auth(analytics_tokens["superadmin"])
    )
    assert listing.status_code == 200
    assert listing.json()["total"] == 2

    metrics = await client.get(
        "/analytics/transfers/metrics", headers=_auth(analytics_tokens["superadmin"])
    )
    assert metrics.status_code == 200
    metrics_payload = metrics.json()
    assert metrics_payload["total_transfers"] == 2
    assert metrics_payload["pending_transfers"] == 1

    bottlenecks = await client.get(
        "/analytics/transfers/bottlenecks",
        params={"warning_days": 1, "critical_days": 2},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert bottlenecks.status_code == 200
    assert bottlenecks.json()["total_bottlenecks"] >= 1


async def test_asset_history_search_and_aggregates(
    client, analytics_seed, analytics_tokens
):
    response = await client.get(
        "/analytics/asset-history/",
        params={"search": "Repair completed"},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1

    aggregates = await client.get(
        "/analytics/asset-history/aggregates",
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert aggregates.status_code == 200
    assert aggregates.json()["total_entries"] >= 1


async def test_top_entities_and_email_masking(client, analytics_seed, analytics_tokens):
    admin_response = await client.get(
        "/analytics/top/users", headers=_auth(analytics_tokens["admin"])
    )
    assert admin_response.status_code == 200
    admin_payload = admin_response.json()
    assert admin_payload
    assert admin_payload[0]["email"]

    analytic_response = await client.get(
        "/analytics/top/users", headers=_auth(analytics_tokens["analytic"])
    )
    assert analytic_response.status_code == 200
    analytic_payload = analytic_response.json()
    assert analytic_payload
    assert analytic_payload[0]["email"] == ""

    assets = await client.get(
        "/analytics/top/assets", headers=_auth(analytics_tokens["superadmin"])
    )
    services = await client.get(
        "/analytics/top/services", headers=_auth(analytics_tokens["superadmin"])
    )
    assert assets.status_code == 200
    assert services.status_code == 200
    assert assets.json()[0]["primary_metric"] == "assignments"
    assert services.json()[0]["service_name"]


async def test_cost_analytics_returns_expected_totals(
    client, analytics_seed, analytics_tokens
):
    repair_costs = await client.get(
        "/analytics/costs/repairs", headers=_auth(analytics_tokens["superadmin"])
    )
    assert repair_costs.status_code == 200
    assert repair_costs.json()["total"] == 2

    asset_costs = await client.get(
        "/analytics/costs/assets", headers=_auth(analytics_tokens["superadmin"])
    )
    assert asset_costs.status_code == 200
    asset_payload = asset_costs.json()
    assert asset_payload["total"] > 0
    assert (
        asset_payload["items"][0]["total_cost"]
        >= asset_payload["items"][0]["purchase_cost"]
    )

    region_costs = await client.get(
        "/analytics/costs/regions", headers=_auth(analytics_tokens["superadmin"])
    )
    assert region_costs.status_code == 200
    assert region_costs.json()["items"][0]["total_cost"] >= 0


async def test_trends_and_forecast_are_deterministic(
    client, analytics_seed, analytics_tokens
):
    trends = await client.get(
        "/analytics/trends/repairs",
        params={"interval": "daily", "periods": 7},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert trends.status_code == 200
    trend_payload = trends.json()
    assert len(trend_payload["points"]) == 7

    forecast_one = await client.get(
        "/analytics/forecast/repairs",
        params={"interval": "weekly", "periods": 4, "basis_window": 2},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    forecast_two = await client.get(
        "/analytics/forecast/repairs",
        params={"interval": "weekly", "periods": 4, "basis_window": 2},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert forecast_one.status_code == 200
    assert forecast_one.json() == forecast_two.json()


async def test_alerts_endpoint_triggers_and_is_configurable(
    client, analytics_seed, analytics_tokens
):
    response = await client.get(
        "/analytics/alerts/",
        params={
            "transfer_days": 1,
            "repair_days": 10,
            "repair_threshold": 1,
            "assignment_threshold": 1,
        },
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert response.status_code == 200
    payload = response.json()
    assert any(item["alert_type"] == "stuck_transfer" for item in payload)
    assert any(item["alert_type"] == "overloaded_user" for item in payload)


async def test_analytics_invalid_params_and_permissions(
    client, analytics_seed, analytics_tokens, monkeypatch
):
    invalid_date = await client.get(
        "/analytics/assignments/",
        params={"date_from": "not-a-date"},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert invalid_date.status_code == 422

    invalid_enum = await client.get(
        "/analytics/transfers/",
        params={"status": "wrong-status"},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert invalid_enum.status_code == 400

    unauthorized = await client.get("/analytics/top/assets")
    assert unauthorized.status_code in {401, 403}

    from api.v1.analytics import top as top_module

    monkeypatch.setattr(top_module, "ANALYTICS_LIMIT", 1)
    monkeypatch.setattr(top_module, "ANALYTICS_WINDOW", 60)

    first = await client.get(
        "/analytics/top/assets",
        params={"limit": 5},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    second = await client.get(
        "/analytics/top/assets",
        params={"limit": 6},
        headers=_auth(analytics_tokens["superadmin"]),
    )
    assert first.status_code == 200
    assert second.status_code == 429
