# api/dependencies/analytics.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.analytics.alert_analytics_repo import AlertAnalyticsRepository
from repositories.analytics.approval_analytics_repo import ApprovalAnalyticsRepository
from repositories.analytics.asset_analytics_repo import AssetAnalyticsRepository
from repositories.analytics.asset_assignment_analytics_repo import AssetAssignmentAnalyticsRepository
from repositories.analytics.asset_history_analytics_repo import AssetHistoryAnalyticsRepository
from repositories.analytics.asset_transfer_analytics_repo import AssetTransferAnalyticsRepository
from repositories.analytics.cost_analytics_repo import CostAnalyticsRepository
from repositories.analytics.document_analytics_repo import DocumentAnalyticsRepository
from repositories.analytics.forecast_analytics_repo import ForecastAnalyticsRepository
from repositories.analytics.region_analytics_repo import RegionAnalyticsRepository
from repositories.analytics.repair_analytics_repo import RepairAnalyticsRepository
from repositories.analytics.top_analytics_repo import TopAnalyticsRepository
from repositories.analytics.transfer_analytics_repo import TransferAnalyticsRepository
from repositories.analytics.trend_analytics_repo import TrendAnalyticsRepository
from repositories.analytics.utilization_analytics_repo import UtilizationAnalyticsRepository

from services.analytics.alert_analytics_service import AlertAnalyticsService
from services.analytics.approval_analytics_service import ApprovalAnalyticsDomainService
from services.analytics.asset_analytics_service import AssetAnalyticsService
from services.analytics.asset_assignment_analytics_service import AssetAssignmentAnalyticsService
from services.analytics.asset_history_analytics_service import AssetHistoryAnalyticsService
from services.analytics.asset_transfer_analytics_service import AssetTransferAnalyticsService
from services.analytics.cost_analytics_service import CostAnalyticsService
from services.analytics.document_analytics_service import DocumentAnalyticsDomainService
from services.analytics.forecast_analytics_service import ForecastAnalyticsService
from services.analytics.region_analytics_service import RegionAnalyticsService
from services.analytics.repair_analytics_service import RepairAnalyticsDomainService
from services.analytics.top_analytics_service import TopAnalyticsService
from services.analytics.transfer_analytics_service import TransferAnalyticsDomainService
from services.analytics.trend_analytics_service import TrendAnalyticsService
from services.analytics.utilization_analytics_service import UtilizationAnalyticsDomainService
from services.analytics.report_service import ReportService


# ============================================================
# ALERTS
# ============================================================
def get_alert_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return AlertAnalyticsRepository(db)


def get_alert_analytics_service(
    repo: AlertAnalyticsRepository = Depends(get_alert_analytics_repo),
) -> AlertAnalyticsService:
    return AlertAnalyticsService(repo)


# ============================================================
# ASSET ANALYTICS
# ============================================================
def get_asset_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return AssetAnalyticsRepository(db)


def get_asset_analytics_service(
    repo: AssetAnalyticsRepository = Depends(get_asset_analytics_repo),
) -> AssetAnalyticsService:
    return AssetAnalyticsService(repo)


# ============================================================
# ASSET ASSIGNMENT ANALYTICS
# ============================================================
def get_asset_assignment_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return AssetAssignmentAnalyticsRepository(db)


def get_asset_assignment_analytics_service(
    repo: AssetAssignmentAnalyticsRepository = Depends(get_asset_assignment_analytics_repo),
) -> AssetAssignmentAnalyticsService:
    return AssetAssignmentAnalyticsService(repo)


# ============================================================
# ASSET HISTORY ANALYTICS
# ============================================================
def get_asset_history_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return AssetHistoryAnalyticsRepository(db)


def get_asset_history_analytics_service(
    repo: AssetHistoryAnalyticsRepository = Depends(get_asset_history_analytics_repo),
) -> AssetHistoryAnalyticsService:
    return AssetHistoryAnalyticsService(repo)


# ============================================================
# ASSET TRANSFER ANALYTICS
# ============================================================
def get_asset_transfer_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return AssetTransferAnalyticsRepository(db)


def get_asset_transfer_analytics_service(
    repo: AssetTransferAnalyticsRepository = Depends(get_asset_transfer_analytics_repo),
) -> AssetTransferAnalyticsService:
    return AssetTransferAnalyticsService(repo)


# ============================================================
# COSTS ANALYTICS
# ============================================================
def get_cost_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return CostAnalyticsRepository(db)


def get_cost_analytics_service(
    repo: CostAnalyticsRepository = Depends(get_cost_analytics_repo),
) -> CostAnalyticsService:
    return CostAnalyticsService(repo)


# ============================================================
# REGION ANALYTICS
# ============================================================
def get_region_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return RegionAnalyticsRepository(db)


def get_region_analytics_service(
    repo: RegionAnalyticsRepository = Depends(get_region_analytics_repo),
) -> RegionAnalyticsService:
    return RegionAnalyticsService(repo)


# ============================================================
# REPAIR ANALYTICS
# ============================================================
def get_repair_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return RepairAnalyticsRepository(db)


def get_repair_analytics_service(
    repo: RepairAnalyticsRepository = Depends(get_repair_analytics_repo),
) -> RepairAnalyticsDomainService:
    return RepairAnalyticsDomainService(repo)


# ============================================================
# TRANSFER ANALYTICS (domain)
# ============================================================
def get_transfer_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return TransferAnalyticsRepository(db)


def get_transfer_analytics_service(
    repo: TransferAnalyticsRepository = Depends(get_transfer_analytics_repo),
) -> TransferAnalyticsDomainService:
    return TransferAnalyticsDomainService(repo)


# ============================================================
# APPROVAL ANALYTICS
# ============================================================
def get_approval_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return ApprovalAnalyticsRepository(db)


def get_approval_analytics_service(
    repo: ApprovalAnalyticsRepository = Depends(get_approval_analytics_repo),
) -> ApprovalAnalyticsDomainService:
    return ApprovalAnalyticsDomainService(repo)


# ============================================================
# DOCUMENT ANALYTICS
# ============================================================
def get_document_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return DocumentAnalyticsRepository(db)


def get_document_analytics_service(
    repo: DocumentAnalyticsRepository = Depends(get_document_analytics_repo),
) -> DocumentAnalyticsDomainService:
    return DocumentAnalyticsDomainService(repo)


# ============================================================
# UTILIZATION ANALYTICS
# ============================================================
def get_utilization_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return UtilizationAnalyticsRepository(db)


def get_utilization_analytics_service(
    repo: UtilizationAnalyticsRepository = Depends(get_utilization_analytics_repo),
) -> UtilizationAnalyticsDomainService:
    return UtilizationAnalyticsDomainService(repo)


# ============================================================
# TOP ANALYTICS
# ============================================================
def get_top_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return TopAnalyticsRepository(db)


def get_top_analytics_service(
    repo: TopAnalyticsRepository = Depends(get_top_analytics_repo),
) -> TopAnalyticsService:
    return TopAnalyticsService(repo)


# ============================================================
# TREND ANALYTICS
# ============================================================
def get_trend_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return TrendAnalyticsRepository(db)


def get_trend_analytics_service(
    repo: TrendAnalyticsRepository = Depends(get_trend_analytics_repo),
) -> TrendAnalyticsService:
    return TrendAnalyticsService(repo)


# ============================================================
# FORECAST ANALYTICS
# ============================================================
def get_forecast_analytics_repo(db: AsyncSession = Depends(get_db_session)):
    return ForecastAnalyticsRepository(db)


def get_forecast_analytics_service(
    repo: ForecastAnalyticsRepository = Depends(get_forecast_analytics_repo),
) -> ForecastAnalyticsService:
    return ForecastAnalyticsService(repo)


# ============================================================
# REPORT SERVICE
# ============================================================
def get_report_service(
    asset_service: AssetAnalyticsService = Depends(get_asset_analytics_service),
    repair_service: RepairAnalyticsDomainService = Depends(get_repair_analytics_service),
    transfer_service: TransferAnalyticsDomainService = Depends(get_transfer_analytics_service),
    approval_service: ApprovalAnalyticsDomainService = Depends(get_approval_analytics_service),
    document_service: DocumentAnalyticsDomainService = Depends(get_document_analytics_service),
    utilization_service: UtilizationAnalyticsDomainService = Depends(get_utilization_analytics_service),
) -> ReportService:
    return ReportService(
        asset_service=asset_service,
        repair_service=repair_service,
        transfer_service=transfer_service,
        approval_service=approval_service,
        document_service=document_service,
        utilization_service=utilization_service,
    )


# Backward compatibility aliases
get_asset_analytics_domain_service = get_asset_analytics_service
get_asset_history_analytics_domain_service = get_asset_history_analytics_service
get_asset_assignment_analytics_domain_service = get_asset_assignment_analytics_service
get_asset_transfer_analytics_domain_service = get_asset_transfer_analytics_service
get_repair_analytics_domain_service = get_repair_analytics_service
get_transfer_analytics_domain_service = get_transfer_analytics_service
get_approval_analytics_domain_service = get_approval_analytics_service
get_document_analytics_domain_service = get_document_analytics_service
get_utilization_analytics_domain_service = get_utilization_analytics_service
