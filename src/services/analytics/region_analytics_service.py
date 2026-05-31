import json
from uuid import UUID

from repositories.analytics.region_analytics_repo import RegionAnalyticsRepository
from schemas.analytics.regions import (
    RegionAssetCostSummaryOut,
    RegionAssetStatusCounts,
    RegionDetailsOut,
    RegionHeatmapPointOut,
    RegionOverviewOut,
    RegionServiceLoadOut,
)
from utils.helpers import utc_now


class RegionAnalyticsService:
    def __init__(self, repo: RegionAnalyticsRepository):
        self.repo = repo

    @staticmethod
    def _to_overview(row) -> RegionOverviewOut:
        geojson = getattr(row, "geojson", None)
        if isinstance(geojson, str):
            try:
                geojson = json.loads(geojson)
            except (TypeError, ValueError):
                geojson = None
        if geojson is not None and not isinstance(geojson, dict):
            geojson = None
        return RegionOverviewOut(
            region_id=row.id,
            region_name=row.name,
            latitude=row.latitude,
            longitude=row.longitude,
            geojson=geojson,
            asset_counts=RegionAssetStatusCounts(
                active=int(row.active_assets or 0),
                assigned=int(row.assigned_assets or 0),
                in_repair=int(row.in_repair_assets or 0),
                archived=int(row.archived_assets or 0),
                total=int(row.total_assets or 0),
            ),
            transfers_in=int(row.transfers_in or 0),
            transfers_out=int(row.transfers_out or 0),
            repairs_count=int(row.repairs_count or 0),
            assignment_load=int(row.assignment_load or 0),
        )

    async def get_overview(self) -> list[RegionOverviewOut]:
        rows = await self.repo.list_overview()
        return [self._to_overview(row) for row in rows]

    async def get_details(self, region_id: UUID) -> RegionDetailsOut | None:
        overview_row, service_rows, cost_rows = await self.repo.get_details(region_id)
        if overview_row is None:
            return None

        overview = self._to_overview(overview_row)
        services = [
            RegionServiceLoadOut(
                service_id=row.id,
                service_name=row.name,
                asset_count=int(row.asset_count or 0),
                active_assignments=int(row.active_assignments or 0),
                repairs_count=int(row.repairs_count or 0),
            )
            for row in service_rows
        ]
        top_cost_assets = [
            RegionAssetCostSummaryOut(
                asset_id=row.id,
                asset_name=row.name,
                purchase_cost=float(row.purchase_cost or 0),
                repair_cost=float(row.repair_cost or 0),
                total_cost=float((row.purchase_cost or 0) + (row.repair_cost or 0)),
            )
            for row in cost_rows
        ]

        return RegionDetailsOut(
            **overview.model_dump(),
            services=services,
            top_cost_assets=top_cost_assets,
        )

    async def get_heatmap(self) -> list[RegionHeatmapPointOut]:
        rows = await self.repo.get_heatmap()
        now = utc_now()
        heatmap = []
        for row in rows:
            total_assets = int(row.total_assets or 0)
            assignment_load = int(row.assignment_load or 0)
            repairs = int(row.repairs_count or 0)
            transfers = int(row.transfers_in or 0) + int(row.transfers_out or 0)
            score = float(
                total_assets + assignment_load * 1.5 + repairs * 2 + transfers
            )
            heatmap.append(
                RegionHeatmapPointOut(
                    region_id=row.id,
                    region_name=row.name,
                    latitude=row.latitude,
                    longitude=row.longitude,
                    geojson=row.geojson,
                    score=score,
                    asset_total=total_assets,
                    active_assignments=assignment_load,
                    repairs_count=repairs,
                    transfers_in=int(row.transfers_in or 0),
                    transfers_out=int(row.transfers_out or 0),
                    updated_at=now,
                )
            )
        return heatmap
