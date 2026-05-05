# api/dependencies/analytics.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.analytics.alert_analytics_repo import AlertAnalyticsRepository
from repositories.analytics.approval_analytics_repo import ApprovalAnalyticsRepository
from repositories.analytics.asset_analytics_repo import AssetAnalyticsRepository
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
from repositories.analytics.document_analytics_repo import DocumentAnalyticsRepository
from repositories.analytics.dashboard.region_repo import RegionAnalyticsRepository
from repositories.analytics.dashboard.repair_repo import (
    RepairAnalyticsRepository as DashboardRepairAnalyticsRepository,
)
from repositories.analytics.dashboard.service_repo import ServiceAnalyticsRepository
from repositories.analytics.dashboard.top_assets_repo import TopAssetsRepository
from repositories.analytics.forecast_analytics_repo import ForecastAnalyticsRepository
from repositories.analytics.region_analytics_repo import (
    RegionAnalyticsRepository as ExtendedRegionAnalyticsRepository,
)
from repositories.analytics.top_analytics_repo import TopAnalyticsRepository
from repositories.analytics.repair_analytics_repo import (
    RepairAnalyticsRepository as DomainRepairAnalyticsRepository,
)
from repositories.analytics.transfer_analytics_repo import TransferAnalyticsRepository
from repositories.analytics.trend_analytics_repo import TrendAnalyticsRepository
from repositories.analytics.utilization_analytics_repo import UtilizationAnalyticsRepository
from services.analytics.alert_analytics_service import AlertAnalyticsService
from services.analytics.alert_service import AnalyticsAlertService
from services.analytics.approval_analytics_service import ApprovalAnalyticsDomainService
from services.analytics.asset_analytics_service import AssetAnalyticsService
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
from services.analytics.document_analytics_service import DocumentAnalyticsDomainService
from services.analytics.dashboard.overview_service import OverviewService
from services.analytics.dashboard.region_service import RegionAnalyticsService
from services.analytics.dashboard.repair_service import RepairAnalyticsService
from services.analytics.dashboard.service_service import ServiceAnalyticsService
from services.analytics.dashboard.top_assets_service import TopAssetsService
from services.analytics.forecast_analytics_service import ForecastAnalyticsService
from services.analytics.report_service import ReportService
from services.analytics.repair_analytics_service import RepairAnalyticsDomainService
from services.analytics.region_analytics_service import (
    RegionAnalyticsService as ExtendedRegionAnalyticsService,
)
from services.analytics.top_analytics_service import TopAnalyticsService
from services.analytics.transfer_analytics_service import TransferAnalyticsDomainService
from services.analytics.trend_analytics_service import TrendAnalyticsService
from services.analytics.utilization_analytics_service import (
    UtilizationAnalyticsDomainService,
)
from services.dashboard.dashboard_service import DashboardService
from api.dependencies.notifications.notification import get_notification_dispatcher
from core.notifications.dispatcher import NotificationDispatcher


def get_repair_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return DashboardRepairAnalyticsRepository(db)


def get_service_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return ServiceAnalyticsRepository(db)


def get_service_analytics_service(
    repo: ServiceAnalyticsRepository = Depends(get_service_analytics_repo),
) -> ServiceAnalyticsService:
    return ServiceAnalyticsService(repo)


def get_repair_analytics_service(
    repo: DashboardRepairAnalyticsRepository = Depends(get_repair_analytics_repo),
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


def get_asset_analytics_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return AssetAnalyticsRepository(db)


def get_asset_analytics_domain_service(
    repo: AssetAnalyticsRepository = Depends(get_asset_analytics_repo),
) -> AssetAnalyticsService:
    return AssetAnalyticsService(repo)


def get_repair_analytics_domain_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return DomainRepairAnalyticsRepository(db)


def get_repair_analytics_domain_service(
    repo: DomainRepairAnalyticsRepository = Depends(get_repair_analytics_domain_repo),
) -> RepairAnalyticsDomainService:
    return RepairAnalyticsDomainService(repo)


def get_transfer_analytics_domain_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return TransferAnalyticsRepository(db)


def get_transfer_analytics_domain_service(
    repo: TransferAnalyticsRepository = Depends(get_transfer_analytics_domain_repo),
) -> TransferAnalyticsDomainService:
    return TransferAnalyticsDomainService(repo)


def get_approval_analytics_domain_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return ApprovalAnalyticsRepository(db)


def get_approval_analytics_domain_service(
    repo: ApprovalAnalyticsRepository = Depends(get_approval_analytics_domain_repo),
) -> ApprovalAnalyticsDomainService:
    return ApprovalAnalyticsDomainService(repo)


def get_document_analytics_domain_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return DocumentAnalyticsRepository(db)


def get_document_analytics_domain_service(
    repo: DocumentAnalyticsRepository = Depends(get_document_analytics_domain_repo),
) -> DocumentAnalyticsDomainService:
    return DocumentAnalyticsDomainService(repo)


def get_utilization_analytics_domain_repo(
    db: AsyncSession = Depends(get_db_session),
):
    return UtilizationAnalyticsRepository(db)


def get_utilization_analytics_domain_service(
    repo: UtilizationAnalyticsRepository = Depends(get_utilization_analytics_domain_repo),
) -> UtilizationAnalyticsDomainService:
    return UtilizationAnalyticsDomainService(repo)


def get_report_service(
    asset_service: AssetAnalyticsService = Depends(get_asset_analytics_domain_service),
    repair_service: RepairAnalyticsDomainService = Depends(get_repair_analytics_domain_service),
    transfer_service: TransferAnalyticsDomainService = Depends(get_transfer_analytics_domain_service),
    approval_service: ApprovalAnalyticsDomainService = Depends(get_approval_analytics_domain_service),
    document_service: DocumentAnalyticsDomainService = Depends(get_document_analytics_domain_service),
    utilization_service: UtilizationAnalyticsDomainService = Depends(get_utilization_analytics_domain_service),
) -> ReportService:
    return ReportService(
        asset_service,
        repair_service,
        transfer_service,
        approval_service,
        document_service,
        utilization_service,
    )


def get_dashboard_service(
    asset_service: AssetAnalyticsService = Depends(get_asset_analytics_domain_service),
    repair_service: RepairAnalyticsDomainService = Depends(get_repair_analytics_domain_service),
    transfer_service: TransferAnalyticsDomainService = Depends(get_transfer_analytics_domain_service),
    approval_service: ApprovalAnalyticsDomainService = Depends(get_approval_analytics_domain_service),
) -> DashboardService:
    return DashboardService(asset_service, repair_service, transfer_service, approval_service)


def get_analytics_alert_service(
    alerts_service: AlertAnalyticsService = Depends(get_alert_analytics_service),
    alerts_repo: AlertAnalyticsRepository = Depends(get_alert_analytics_repo),
    notification_dispatcher: NotificationDispatcher = Depends(get_notification_dispatcher),
) -> AnalyticsAlertService:
    return AnalyticsAlertService(alerts_service, alerts_repo, notification_dispatcher)
