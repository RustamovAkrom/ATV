from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_transfer import AssetTransfer
from db.models.enums import AssetStatus
from db.models.org.region import Region
from db.models.org.service import Service, region_services
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart


class RegionAnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _asset_counts_subquery(self):
        return (
            select(
                Asset.region_id.label("region_id"),
                func.count(Asset.id).label("total_assets"),
                func.count(Asset.id)
                .filter(Asset.status == AssetStatus.ACTIVE)
                .label("active_assets"),
                func.count(Asset.id)
                .filter(Asset.status == AssetStatus.ASSIGNED)
                .label("assigned_assets"),
                func.count(Asset.id)
                .filter(Asset.status == AssetStatus.IN_REPAIR)
                .label("in_repair_assets"),
                func.count(Asset.id)
                .filter(Asset.status == AssetStatus.ARCHIVED)
                .label("archived_assets"),
            )
            .where(Asset.region_id.isnot(None))
            .group_by(Asset.region_id)
            .subquery()
        )

    def _repair_counts_subquery(self):
        return (
            select(
                Asset.region_id.label("region_id"),
                func.count(Repair.id).label("repairs_count"),
            )
            .join(Asset, Asset.id == Repair.asset_id)
            .where(Asset.region_id.isnot(None))
            .group_by(Asset.region_id)
            .subquery()
        )

    def _assignment_load_subquery(self):
        return (
            select(
                Asset.region_id.label("region_id"),
                func.count(AssetAssignment.id).label("assignment_load"),
            )
            .join(Asset, Asset.id == AssetAssignment.asset_id)
            .where(
                Asset.region_id.isnot(None),
                AssetAssignment.unassigned_at.is_(None),
            )
            .group_by(Asset.region_id)
            .subquery()
        )

    def _transfer_counts_subquery(self):
        inbound = (
            select(
                region_services.c.region_id.label("region_id"),
                func.count(AssetTransfer.id).label("transfers_in"),
            )
            .select_from(region_services)
            .join(Service, Service.id == region_services.c.service_id)
            .join(AssetTransfer, AssetTransfer.to_service_id == Service.id)
            .group_by(region_services.c.region_id)
            .subquery()
        )

        outbound = (
            select(
                region_services.c.region_id.label("region_id"),
                func.count(AssetTransfer.id).label("transfers_out"),
            )
            .select_from(region_services)
            .join(Service, Service.id == region_services.c.service_id)
            .join(AssetTransfer, AssetTransfer.from_service_id == Service.id)
            .group_by(region_services.c.region_id)
            .subquery()
        )

        return inbound, outbound

    async def list_overview(self):
        asset_counts = self._asset_counts_subquery()
        repair_counts = self._repair_counts_subquery()
        assignment_load = self._assignment_load_subquery()
        transfers_in, transfers_out = self._transfer_counts_subquery()

        result = await self.session.execute(
            select(
                Region.id,
                Region.name,
                Region.latitude,
                Region.longitude,
                Region.geojson,
                func.coalesce(asset_counts.c.total_assets, 0).label("total_assets"),
                func.coalesce(asset_counts.c.active_assets, 0).label("active_assets"),
                func.coalesce(asset_counts.c.assigned_assets, 0).label(
                    "assigned_assets"
                ),
                func.coalesce(asset_counts.c.in_repair_assets, 0).label(
                    "in_repair_assets"
                ),
                func.coalesce(asset_counts.c.archived_assets, 0).label(
                    "archived_assets"
                ),
                func.coalesce(repair_counts.c.repairs_count, 0).label("repairs_count"),
                func.coalesce(assignment_load.c.assignment_load, 0).label(
                    "assignment_load"
                ),
                func.coalesce(transfers_in.c.transfers_in, 0).label("transfers_in"),
                func.coalesce(transfers_out.c.transfers_out, 0).label("transfers_out"),
            )
            .outerjoin(asset_counts, asset_counts.c.region_id == Region.id)
            .outerjoin(repair_counts, repair_counts.c.region_id == Region.id)
            .outerjoin(assignment_load, assignment_load.c.region_id == Region.id)
            .outerjoin(transfers_in, transfers_in.c.region_id == Region.id)
            .outerjoin(transfers_out, transfers_out.c.region_id == Region.id)
            # Keep one row per region by joining pre-aggregated subqueries only.
            .order_by(Region.name.asc())
        )
        return result.all()

    async def get_details(self, region_id):
        overview_rows = await self.list_overview()
        overview = next((row for row in overview_rows if row.id == region_id), None)
        if overview is None:
            return None, [], []

        service_rows = await self.session.execute(
            select(
                Service.id,
                Service.name,
                func.count(func.distinct(Asset.id)).label("asset_count"),
                func.count(func.distinct(AssetAssignment.id))
                .filter(AssetAssignment.unassigned_at.is_(None))
                .label("active_assignments"),
                func.count(func.distinct(Repair.id)).label("repairs_count"),
            )
            .select_from(region_services)
            .join(Service, Service.id == region_services.c.service_id)
            .outerjoin(Asset, Asset.service_id == Service.id)
            .outerjoin(
                AssetAssignment,
                (AssetAssignment.asset_id == Asset.id)
                & AssetAssignment.unassigned_at.is_(None),
            )
            .outerjoin(Repair, Repair.asset_id == Asset.id)
            .where(region_services.c.region_id == region_id)
            .group_by(Service.id, Service.name)
            .order_by(Service.name.asc())
        )

        repair_parts = (
            select(
                RepairPart.repair_id.label("repair_id"),
                func.sum(RepairPart.quantity * RepairPart.unit_price).label(
                    "parts_cost"
                ),
            )
            .group_by(RepairPart.repair_id)
            .subquery()
        )
        repair_costs = (
            select(
                Repair.asset_id.label("asset_id"),
                func.sum(
                    func.coalesce(Repair.labor_cost, 0)
                    + func.coalesce(repair_parts.c.parts_cost, 0)
                ).label("repair_cost"),
            )
            .outerjoin(repair_parts, repair_parts.c.repair_id == Repair.id)
            .group_by(Repair.asset_id)
            .subquery()
        )

        cost_rows = await self.session.execute(
            select(
                Asset.id,
                Asset.name,
                Asset.asset_tag,
                func.coalesce(Asset.purchase_cost, 0).label("purchase_cost"),
                func.coalesce(repair_costs.c.repair_cost, 0).label("repair_cost"),
            )
            .outerjoin(repair_costs, repair_costs.c.asset_id == Asset.id)
            .where(Asset.region_id == region_id)
            # Pre-aggregate repair costs per asset to prevent
            # join fan-out from inflating totals.
            .group_by(
                Asset.id,
                Asset.name,
                Asset.asset_tag,
                Asset.purchase_cost,
                repair_costs.c.repair_cost,
            )
            .order_by(
                (
                    func.coalesce(Asset.purchase_cost, 0)
                    + func.coalesce(repair_costs.c.repair_cost, 0)
                ).desc()
            )
            .limit(5)
        )

        return overview, service_rows.all(), cost_rows.all()

    async def get_heatmap(self):
        return await self.list_overview()
