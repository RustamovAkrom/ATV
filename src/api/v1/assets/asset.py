from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from api.dependencies.assets.asset import (
    get_asset_service,
    get_bulk_asset_service,
)
from api.dependencies.assets.asset_export import get_export_service
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from core.slowapi import limiter
from db.models.enums import AssetStatus
from schemas.assets.assets import (
    AssetCreate,
    AssetDetailSchema,
    AssetFilters,
    AssetHistorySchema,
    AssetPage,
    AssetStatusChangeRequest,
    AssetUpdate,
)
from schemas.assets.bulk import (
    BulkAssignRequest,
    BulkResult,
    BulkStatusRequest,
    BulkTransferRequest,
)
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from schemas.pagination import PaginationParamsSchema
from services.assets.asset_service import AssetService
from services.assets.bulk_asset_service import BulkAssetService
from services.assets.export_service import ExportService

router = APIRouter(prefix="/assets", tags=["Assets"])


def get_asset_filters(
    owner_id: UUID | None = Query(None),
    region_id: UUID | None = Query(None),
    service_id: UUID | None = Query(None),
    class_id: UUID | None = Query(None),
    manufacturer_id: UUID | None = Query(None),
    category_id: UUID | None = Query(None),
    status: AssetStatus | None = Query(None),
    search: str | None = Query(None),
) -> AssetFilters:
    return AssetFilters(
        owner_id=owner_id,
        region_id=region_id,
        service_id=service_id,
        class_id=class_id,
        manufacturer_id=manufacturer_id,
        category_id=category_id,
        status=status,
        search=search,
    )


@router.get(
    "/",
    response_model=AssetPage,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=30, tags=("asset:list",))
async def list_assets(
    filters: AssetFilters = Depends(get_asset_filters),
    pagination: PaginationParamsSchema = Depends(),
    service: AssetService = Depends(get_asset_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list(filters, pagination, actor)


@router.get(
    "/export",
    dependencies=[Depends(AssetPermissions.CanExportAssets)]
)
async def export_assets(
    filters: AssetFilters = Depends(get_asset_filters),
    format: str = Query("csv", pattern="^(csv|json)$"),
    service: ExportService = Depends(get_export_service),
):
    await service.ensure_exportable(filters)
    media_type = "text/csv" if format == "csv" else "application/json"
    filename = f"assets_export.{format}"
    return StreamingResponse(
        service.stream_assets(filters, format),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{asset_id}",
    response_model=AssetDetailSchema,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(tags=("asset:detail",))
async def get_asset(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    return await service.get(asset_id, actor)


@router.get(
    "/{asset_id}/history",
    response_model=list[AssetHistorySchema],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(tags=("asset:history",))
async def get_asset_history(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    return await service.get_history(asset_id, actor)


@router.post(
    "/",
    response_model=AssetDetailSchema,
    dependencies=[Depends(AssetPermissions.CanCreateAssets)],
)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:history",
    )
)
async def create_asset(
    request: Request,
    data: AssetCreate,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.create(data, actor)


@router.post(
    "/bulk/assign",
    response_model=BulkResult,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("15/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:history",
        "asset:detail",
    )
)
async def bulk_assign_assets(
    request: Request,
    data: BulkAssignRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_assign(
        data.asset_ids, data.user_id, actor, atomic=data.atomic
    )


@router.post(
    "/bulk/transfer",
    response_model=BulkResult,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("15/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:history",
        "asset:detail",
    )
)
async def bulk_transfer_assets(
    request: Request,
    data: BulkTransferRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_transfer(
        data.asset_ids, data.transfer, actor, atomic=data.atomic
    )


@router.post(
    "/bulk/status",
    response_model=BulkResult,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@limiter.limit("15/minute")
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:history",
        "asset:detail",
    )
)
async def bulk_update_asset_status(
    request: Request,
    data: BulkStatusRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_update_status(
        data.asset_ids, data.status, actor, atomic=data.atomic
    )


@router.patch(
    "/{asset_id}",
    response_model=AssetDetailSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:history",
        "asset:detail",
    )
)
async def update_asset(
    asset_id: UUID,
    data: AssetUpdate,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.update(asset_id, data, actor)


@router.delete(
    "/{asset_id}",
    response_model=StatusResponse,
    dependencies=[Depends(AssetPermissions.CanDeleteAssets)],
)
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:history",
        "asset:detail",
    )
)
async def delete_asset(
    asset_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    await service.delete(asset_id, actor)
    return StatusResponse(status="deleted", message="Asset deleted successfully")


@router.post(
    "/{asset_id}/status",
    response_model=AssetDetailSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@invalidate_cache(
    tags=(
        "asset:list",
        "asset:export",
        "asset:history",
        "asset:detail",
    )
)
async def change_asset_status(
    asset_id: UUID,
    data: AssetStatusChangeRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.change_status(asset_id, data, actor)
