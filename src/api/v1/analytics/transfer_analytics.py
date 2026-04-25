# api/v1/analytics/transfer_analytics.py

from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, Request

from schemas.analytics.asset_transfer_analytics import (
    AssetTransferFilterInput,
    AssetTransferPageOut,
    AssetTransferOut,
    AssetTransferHistory,
    TransferMetrics,
    BottleneckReportOut,
    WarehouseTransferMetrics,
)
from schemas.pagination import PaginationParams, PageOut
from services.analytics.asset_transfer_analytics_service import (
    AssetTransferAnalyticsService,
)
from api.dependencies.analytics import get_asset_transfer_analytics_service
from api.v1.analytics._utils import enforce_rate_limit, parse_optional_datetime, parse_rate_limit, run_analytics_operation
from core.config import get_settings
from core.security.rbac import presets
from core.cache.decorators import cached
from db.models.enums import TransferStatus
from schemas.pagination import build_page

router = APIRouter(
    prefix="/analytics/transfers",
    tags=["Analytics - Asset Transfers"],
)
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get(
    "/",
    response_model=PageOut[AssetTransferOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=60, tags=("analytics:transfers:list",))
async def list_transfers(
    request: Request,
    asset_id: UUID | None = Query(None),
    created_by_id: UUID | None = Query(None),
    received_by_id: UUID | None = Query(None),
    from_warehouse_id: UUID | None = Query(None),
    to_warehouse_id: UUID | None = Query(None),
    from_service_id: UUID | None = Query(None),
    to_service_id: UUID | None = Query(None),
    status: TransferStatus | None = Query(None, description="pending, completed, or cancelled"),
    date_from: str | None = Query(None, description="ISO format datetime"),
    date_to: str | None = Query(None, description="ISO format datetime"),
    search: str | None = Query(None, max_length=100),
    pagination: PaginationParams = Depends(),
    service: AssetTransferAnalyticsService = Depends(get_asset_transfer_analytics_service),
):
    """List asset transfers with filtering and pagination."""
    date_from_dt = parse_optional_datetime(date_from)
    date_to_dt = parse_optional_datetime(date_to)

    filters = AssetTransferFilterInput(
        asset_id=asset_id,
        created_by_id=created_by_id,
        received_by_id=received_by_id,
        from_warehouse_id=from_warehouse_id,
        to_warehouse_id=to_warehouse_id,
        from_service_id=from_service_id,
        to_service_id=to_service_id,
        status=status,
        date_from=date_from_dt,
        date_to=date_to_dt,
        search=search,
    )

    await enforce_rate_limit(request, "analytics:transfers:list", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.transfers.list",
        filters.model_dump(mode="json"),
        lambda: service.list_transfers(filters, pagination),
        lambda: build_page(schema=PageOut[AssetTransferOut], items=[], total=0, page=pagination.page, limit=pagination.limit),
    )


@router.get(
    "/pending",
    response_model=PageOut[AssetTransferOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=30, tags=("analytics:transfers:pending",))
async def list_pending_transfers(
    request: Request,
    pagination: PaginationParams = Depends(),
    service: AssetTransferAnalyticsService = Depends(get_asset_transfer_analytics_service),
):
    """List pending transfers (waiting for completion)."""
    await enforce_rate_limit(request, "analytics:transfers:pending", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.transfers.pending",
        {"page": pagination.page, "limit": pagination.limit},
        lambda: service.list_pending_transfers(pagination),
        lambda: build_page(schema=PageOut[AssetTransferOut], items=[], total=0, page=pagination.page, limit=pagination.limit),
    )


@router.get(
    "/asset/{asset_id}/history",
    response_model=AssetTransferHistory,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=300, tags=("analytics:transfers:history",))
async def get_asset_transfer_history(
    request: Request,
    asset_id: UUID,
    service: AssetTransferAnalyticsService = Depends(get_asset_transfer_analytics_service),
):
    """Get complete transfer history for an asset."""
    await enforce_rate_limit(request, "analytics:transfers:history", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.transfers.history",
        {"asset_id": asset_id},
        lambda: service.get_asset_transfer_history(asset_id),
        lambda: AssetTransferHistory(asset_id=asset_id, asset_name="Unknown", total_transfers=0, completed_transfers=0, pending_transfers=0, cancelled_transfers=0, history=[]),
    )


@router.get(
    "/metrics",
    response_model=TransferMetrics,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=600, tags=("analytics:transfers:metrics",))
async def get_transfer_metrics(
    request: Request,
    asset_id: UUID | None = Query(None),
    created_by_id: UUID | None = Query(None),
    status: TransferStatus | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    service: AssetTransferAnalyticsService = Depends(get_asset_transfer_analytics_service),
):
    """Get aggregated transfer metrics."""
    date_from_dt = parse_optional_datetime(date_from)
    date_to_dt = parse_optional_datetime(date_to)

    filters = AssetTransferFilterInput(
        asset_id=asset_id,
        created_by_id=created_by_id,
        status=status,
        date_from=date_from_dt,
        date_to=date_to_dt,
    )

    await enforce_rate_limit(request, "analytics:transfers:metrics", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.transfers.metrics",
        filters.model_dump(mode="json"),
        lambda: service.get_transfer_metrics(filters),
        lambda: TransferMetrics(
            total_transfers=0,
            completed_transfers=0,
            pending_transfers=0,
            cancelled_transfers=0,
            average_completion_time_days=Decimal(0),
            longest_completion_time_days=Decimal(0),
            shortest_completion_time_days=Decimal(0),
            oldest_pending_transfer_days=0,
            oldest_pending_transfer_id=None,
            transfers_pending_over_7_days=0,
            transfers_pending_over_30_days=0,
            status_breakdown=[],
        ),
    )


@router.get(
    "/bottlenecks",
    response_model=BottleneckReportOut,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=300, tags=("analytics:transfers:bottlenecks",))
async def get_transfer_bottlenecks(
    request: Request,
    critical_days: int = Query(30, ge=1),
    warning_days: int = Query(7, ge=1),
    service: AssetTransferAnalyticsService = Depends(get_asset_transfer_analytics_service),
):
    """Get transfer bottleneck report (transfers pending too long)."""
    await enforce_rate_limit(request, "analytics:transfers:bottlenecks", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.transfers.bottlenecks",
        {"critical_days": critical_days, "warning_days": warning_days},
        lambda: service.get_bottleneck_report(critical_days, warning_days),
        lambda: BottleneckReportOut(total_bottlenecks=0, critical_bottlenecks=[], warning_bottlenecks=[]),
    )


@router.get(
    "/warehouse/{warehouse_id}/metrics",
    response_model=WarehouseTransferMetrics,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=600, tags=("analytics:transfers:warehouse",))
async def get_warehouse_transfer_metrics(
    request: Request,
    warehouse_id: UUID,
    service: AssetTransferAnalyticsService = Depends(get_asset_transfer_analytics_service),
):
    """Get transfer metrics for a specific warehouse."""
    await enforce_rate_limit(request, "analytics:transfers:warehouse", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.transfers.warehouse_metrics",
        {"warehouse_id": warehouse_id},
        lambda: service.get_warehouse_metrics(warehouse_id),
        lambda: WarehouseTransferMetrics(
            warehouse_id=warehouse_id,
            warehouse_name="Unknown",
            transfers_from=0,
            transfers_to=0,
            pending_in=0,
            pending_out=0,
            average_duration_days=Decimal(0),
        ),
    )
