# api/dependencies/analytics.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.analytics.alert_analytics_repo import AlertAnalyticsRepository
from repositories.analytics.asset_assignment_analytics_repo import (
    AssetAssignmentAnalyticsRepository,
)
from repositories.analytics.asset_history_analytics_repo import (
    AssetHistoryAnalyticsRepository,
)
from repositories.analytics.asset_transfer_analytics_repo import (
    AssetTransferAnalyticsRepository,
)
from repositories.analytics.cost_analytics_repo import CostAnalyticsRepository
from repositories.analytics.dashboard.region_repo import RegionAnalyticsRepository
from repositories.analytics.dashboard.repair_repo import RepairAnalyticsRepository
from repositories.analytics.dashboard.service_repo import ServiceAnalyticsRepository
from repositories.analytics.dashboard.top_assets_repo import TopAssetsRepository
from repositories.analytics.forecast_analytics_repo import ForecastAnalyticsRepository
from repositories.analytics.region_analytics_repo import (
    RegionAnalyticsRepository as ExtendedRegionAnalyticsRepository,
)
from repositories.analytics.top_analytics_repo import TopAnalyticsRepository
from repositories.analytics.trend_analytics_repo import TrendAnalyticsRepository
from services.analytics.alert_analytics_service import AlertAnalyticsService
from services.analytics.asset_assignment_analytics_service import (
    AssetAssignmentAnalyticsService,
)
from services.analytics.asset_history_analytics_service import (
    AssetHistoryAnalyticsService,
)
from services.analytics.asset_transfer_analytics_service import (
    AssetTransferAnalyticsService,
)
from services.analytics.cost_analytics_service import CostAnalyticsService
from services.analytics.dashboard.overview_service import OverviewService
from services.analytics.dashboard.region_service import RegionAnalyticsService
from services.analytics.dashboard.repair_service import RepairAnalyticsService
from services.analytics.dashboard.service_service import ServiceAnalyticsService
from services.analytics.dashboard.top_assets_service import TopAssetsService
from services.analytics.forecast_analytics_service import ForecastAnalyticsService
from services.analytics.region_analytics_service import (
    RegionAnalyticsService as ExtendedRegionAnalyticsService,
)
from services.analytics.top_analytics_service import TopAnalyticsService
from services.analytics.trend_analytics_service import TrendAnalyticsService


def get_repair_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return RepairAnalyticsRepository(db)


def get_service_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return ServiceAnalyticsRepository(db)


def get_service_analytics_service(
    repo: ServiceAnalyticsRepository = Depends(get_service_analytics_repo),
) -> ServiceAnalyticsService:
    return ServiceAnalyticsService(repo)


def get_repair_analytics_service(
    repo: RepairAnalyticsRepository = Depends(get_repair_analytics_repo),
) -> RepairAnalyticsService:
    return RepairAnalyticsService(repo)


def get_region_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return RegionAnalyticsRepository(db)


def get_region_analytics_service(
    repo: RegionAnalyticsRepository = Depends(get_region_analytics_repo),
):
    return RegionAnalyticsService(repo)


def get_top_assets_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return TopAssetsRepository(db)


def get_top_assets_service(
    repo: TopAssetsRepository = Depends(get_top_assets_repo),
):
    return TopAssetsService(repo)


# Asset History
def get_asset_history_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return AssetHistoryAnalyticsRepository(db)


def get_asset_history_analytics_service(
    repo: AssetHistoryAnalyticsRepository = Depends(get_asset_history_analytics_repo),
):
    return AssetHistoryAnalyticsService(repo)


# Asset Assignment
def get_asset_assignment_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return AssetAssignmentAnalyticsRepository(db)


def get_asset_assignment_analytics_service(
    repo: AssetAssignmentAnalyticsRepository = Depends(
        get_asset_assignment_analytics_repo
    ),
):
    return AssetAssignmentAnalyticsService(repo)


# Asset Transfer
def get_asset_transfer_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return AssetTransferAnalyticsRepository(db)


def get_asset_transfer_analytics_service(
    repo: AssetTransferAnalyticsRepository = Depends(get_asset_transfer_analytics_repo),
):
    return AssetTransferAnalyticsService(repo)


def get_overview_service(
    assignment_service=Depends(get_asset_assignment_analytics_service),
    transfer_service=Depends(get_asset_transfer_analytics_service),
    history_service=Depends(get_asset_history_analytics_service),
):
    return OverviewService(
        assignment_service,
        transfer_service,
        history_service,
    )


def get_extended_region_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return ExtendedRegionAnalyticsRepository(db)


def get_extended_region_analytics_service(
    repo: ExtendedRegionAnalyticsRepository = Depends(
        get_extended_region_analytics_repo
    ),
):
    return ExtendedRegionAnalyticsService(repo)


def get_top_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return TopAnalyticsRepository(db)


def get_top_analytics_service(
    repo: TopAnalyticsRepository = Depends(get_top_analytics_repo),
):
    return TopAnalyticsService(repo)


def get_cost_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return CostAnalyticsRepository(db)


def get_cost_analytics_service(
    repo: CostAnalyticsRepository = Depends(get_cost_analytics_repo),
):
    return CostAnalyticsService(repo)


def get_trend_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return TrendAnalyticsRepository(db)


def get_trend_analytics_service(
    repo: TrendAnalyticsRepository = Depends(get_trend_analytics_repo),
):
    return TrendAnalyticsService(repo)


def get_forecast_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return ForecastAnalyticsRepository(db)


def get_forecast_analytics_service(
    repo: ForecastAnalyticsRepository = Depends(get_forecast_analytics_repo),
):
    return ForecastAnalyticsService(repo)


def get_alert_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return AlertAnalyticsRepository(db)


def get_alert_analytics_service(
    repo: AlertAnalyticsRepository = Depends(get_alert_analytics_repo),
):
    return AlertAnalyticsService(repo)
