from datetime import UTC, datetime
from uuid import uuid4

from schemas.analytics.approval import ApprovalAnalyticsDataSchema
from schemas.analytics.asset import (
    AssetDistributionDataSchema,
    AssetLifecycleDataSchema,
    RegionGeoMetricSchema,
)
from schemas.analytics.base import (
    AnalyticsFilters,
    AnalyticsPageOut,
    DurationMetrics,
    TransferDurationMetrics,
)
from schemas.analytics.document import DocumentAnalyticsDataSchema
from schemas.analytics.repair import RepairAnalyticsDataSchema, RepairAssetMetricSchema
from schemas.analytics.report import OverviewDataSchema, ReportDataSchema
from schemas.analytics.transfer import (
    TransferAnalyticsDataSchema,
    TransferAssetMetricSchema,
)
from schemas.analytics.utilization import (
    UtilizationAnalyticsDataSchema,
    UtilizationEmployeeSchema,
    UtilizationRegionLoadSchema,
    UtilizationServiceSchema,
)


def test_analytics_schema_models_roundtrip():
    approval = ApprovalAnalyticsDataSchema(
        pending_approvals=1,
        average_approval_time_hours=2.5,
        rejection_rate=10.0,
    )
    assert approval.pending_approvals == 1

    geo = RegionGeoMetricSchema(
        region_id="r1", region_name="Region", metrics={"active": 2}
    )
    dist = {"labels": ["a"], "values": [1]}
    asset_dist = AssetDistributionDataSchema(
        total_assets=2,
        by_region=dist,
        by_service=dist,
        by_warehouse=dist,
        by_status=dist,
        geo=[geo],
    )
    assert asset_dist.total_assets == 2

    lifecycle = AssetLifecycleDataSchema(
        lifecycle_distribution=dist, critical_assets_percentage=12.0
    )
    assert lifecycle.critical_assets_percentage == 12.0

    filters = AnalyticsFilters(
        region_id=uuid4(),
        service_id=uuid4(),
        date_from=datetime.now(UTC),
        date_to=datetime.now(UTC),
    )
    page = AnalyticsPageOut[str](items=["x"], total=3, page=1, limit=2)
    assert filters.region_id is not None
    assert page.pages == 2
    assert page.has_next is True
    assert page.has_prev is False

    duration = DurationMetrics(duration_days=1, duration_formatted="1d")
    transfer_duration = TransferDurationMetrics(
        duration_days=1,
        duration_formatted="1d",
        pending_duration_days=1,
        pending_duration_formatted="1d",
        total_duration_days=2,
        total_duration_formatted="2d",
        days_to_completion=1,
        is_pending=False,
    )
    assert duration.duration_formatted == "1d"
    assert transfer_duration.is_pending is False

    document = DocumentAnalyticsDataSchema(
        total_assets=10,
        with_documents=8,
        without_documents=2,
        missing_compliance_documentation=1,
    )
    assert document.with_documents == 8

    repair_asset = RepairAssetMetricSchema(
        asset_id="a1", asset_name="Asset", repair_count=2, total_repair_cost=100.0
    )
    repair = RepairAnalyticsDataSchema(
        average_repair_cost=50.0,
        per_asset=[repair_asset],
        abnormal_repair_frequency_assets=[repair_asset],
    )
    assert repair.per_asset[0].repair_count == 2

    report = ReportDataSchema(summary={}, breakdowns={}, trends={})
    overview = OverviewDataSchema(kpis=[], breakdowns={}, trends={})
    assert report.summary == {}
    assert overview.kpis == []

    t_asset = TransferAssetMetricSchema(
        asset_id="a1", asset_name="Asset", transfer_count=3
    )
    transfer = TransferAnalyticsDataSchema(
        transfers_per_period={"labels": ["d1"], "values": [1]},
        most_moved_assets=[t_asset],
        unstable_assets=[t_asset],
    )
    assert transfer.most_moved_assets[0].transfer_count == 3

    ue = UtilizationEmployeeSchema(user_id="u1", user_name="User", asset_count=3)
    us = UtilizationServiceSchema(
        service_id="s1", service_name="Service", asset_count=5
    )
    ur = UtilizationRegionLoadSchema(
        region_id="r1",
        region_name="Region",
        asset_count=10,
        employee_count=2,
        load_ratio=5.0,
    )
    util = UtilizationAnalyticsDataSchema(
        assets_per_employee=[ue],
        assets_per_service=[us],
        overloaded_regions=[ur],
        underutilized_regions=[ur],
    )
    assert util.overloaded_regions[0].load_ratio == 5.0
