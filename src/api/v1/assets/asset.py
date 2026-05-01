from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from api.dependencies.assets.assets import (
    get_asset_service,
    get_bulk_asset_service,
)
from api.dependencies.assets.asset_export import get_export_service
from api.dependencies.assets.asset_repair import get_repair_service
from api.dependencies.assets.asset_warehouse import get_warehouse_service
from api.dependencies.documents.document import get_document_service

from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
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
from schemas.auth import CurrentUserSchema
from schemas.assets.bulk import (
    BulkAssignRequest,
    BulkResult,
    BulkStatusRequest,
    BulkTransferRequest,
)
from schemas.documents import AssetDocumentCreate, AssetDocumentSchema
from schemas.pagination import PaginationParamsSchema
from schemas.assets.repairs import (
    RepairCancelRequest,
    RepairReportRequest,
    RepairSchema,
    RepairStartRequest,
)
from schemas.assets.warehouses import WarehouseMoveRequest
from services.assets.asset_service import AssetService
from services.assets.bulk_asset_service import BulkAssetService
from services.documents.document_service import DocumentService
from services.assets.export_service import ExportService
from services.assets.repair_service import RepairService
from services.assets.warehouse_service import WarehouseService

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


@router.get("/", response_model=AssetPage, dependencies=[presets.CanViewAssets])
@cached(ttl=30, tags=("assets:list",))
async def list_assets(
    filters: AssetFilters = Depends(get_asset_filters),
    pagination: PaginationParamsSchema = Depends(),
    service: AssetService = Depends(get_asset_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list(filters, pagination, actor)


@router.post(
    "/", response_model=AssetDetailSchema, dependencies=[presets.CanCreateAssets]
)
@invalidate_cache(tags=("assets:list",))
async def create_asset(
    data: AssetCreate,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.create(data, actor)


@router.post(
    "/bulk/assign", response_model=BulkResult, dependencies=[presets.CanUpdateAssets]
)
@invalidate_cache(tags=("assets:list",))
async def bulk_assign_assets(
    data: BulkAssignRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_assign(data.asset_ids, data.user_id, actor)


@router.post(
    "/bulk/transfer", response_model=BulkResult, dependencies=[presets.CanUpdateAssets]
)

@invalidate_cache(tags=("assets:list",))
async def bulk_transfer_assets(
    data: BulkTransferRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_transfer(data.asset_ids, data.transfer, actor)


@router.post(
    "/bulk/status", response_model=BulkResult, dependencies=[presets.CanUpdateAssets]
)
@invalidate_cache(tags=("assets:list",))
async def bulk_update_asset_status(
    data: BulkStatusRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_update_status(
        data.asset_ids, data.status, actor
    )


@router.get("/export", dependencies=[presets.CanExportAssets])
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
    dependencies=[presets.CanViewAssets],
)
async def get_asset(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    return await service.get(asset_id, actor)


@router.patch(
    "/{asset_id}",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def update_asset(
    asset_id: UUID,
    data: AssetUpdate,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.update(asset_id, data, actor)


@router.delete("/{asset_id}", dependencies=[presets.CanDeleteAssets])
@invalidate_cache(tags=("assets:list",))
async def delete_asset(
    asset_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    await service.delete(asset_id, actor)
    return {"status": "deleted"}


@router.post(
    "/{asset_id}/status",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def change_asset_status(
    asset_id: UUID,
    data: AssetStatusChangeRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.change_status(asset_id, data, actor)


@router.get(
    "/{asset_id}/history",
    response_model=list[AssetHistorySchema],
    dependencies=[presets.CanViewAssets],
)
async def get_asset_history(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    return await service.get_history(asset_id, actor)

# @router.post(
#     "/{asset_id}/request-assignment",
#     response_model=ApprovalSchema,
#     dependencies=[presets.CanCreateApprovals],
# )
# async def request_asset_assignment(
#     asset_id: UUID,
#     data: AssetAssignmentRequest,
#     current_user: CurrentUserSchema = Depends(get_current_user),
#     approval_service: ApprovalService = Depends(get_approval_service),
# ):
#     return await approval_service.create(
#         ApprovalCreate(
#             entity_type="asset_assignment",
#             entity_id=asset_id,
#             action="assign",
#             payload={"user_id": str(data.user_id)},
#         ),
#         current_user.id,
#     )



# @router.post(
#     "/{asset_id}/request-transfer",
#     response_model=ApprovalSchema,
#     dependencies=[presets.CanCreateApprovals],
# )
# async def request_transfer(
#     asset_id: UUID,
#     data: AssetTransferCreate,
#     current_user: CurrentUserSchema = Depends(get_current_user),
#     approval_service: ApprovalService = Depends(get_approval_service),
# ):
#     return await approval_service.create(
#         ApprovalCreate(
#             entity_type="asset_transfer",
#             entity_id=asset_id,
#             action="create_transfer",
#             payload=data.model_dump(exclude_none=True),
#         ),
#         current_user.id,
#     )


# @router.post(
#     "/{asset_id}/repair/report",
#     response_model=RepairSchema,
#     dependencies=[presets.CanUpdateAssets],
# )
# @invalidate_cache(tags=("assets:list",))
# async def report_asset_repair(
#     asset_id: UUID,
#     data: RepairReportRequest,
#     actor: CurrentUserSchema = Depends(get_current_user),
#     service: RepairService = Depends(get_repair_service),
# ):
#     return await service.report_repair(asset_id, data, actor)
# @router.post(
#     "/{asset_id}/repair/{repair_id}/start",
#     response_model=RepairSchema,
#     dependencies=[presets.CanUpdateAssets],
# )


# @invalidate_cache(tags=("assets:list",))
# async def start_asset_repair(
#     asset_id: UUID,
#     repair_id: UUID,
#     data: RepairStartRequest,
#     actor: CurrentUserSchema = Depends(get_current_user),
#     service: RepairService = Depends(get_repair_service),
# ):
#     return await service.start_repair(asset_id, repair_id, data, actor)


# @router.post(
#     "/{asset_id}/request-repair-complete",
#     response_model=ApprovalSchema,
#     dependencies=[presets.CanCreateApprovals],
# )
# async def request_repair_complete(
#     asset_id: UUID,
#     repair_id: UUID,
#     data: RepairCompleteRequest,
#     current_user: CurrentUserSchema = Depends(get_current_user),
#     approval_service: ApprovalService = Depends(get_approval_service),
# ):
#     payload = data.model_dump(exclude_none=True)
#     payload["repair_id"] = str(repair_id)

#     return await approval_service.create(
#         ApprovalCreate(
#             entity_type="repair",
#             entity_id=asset_id,
#             action="complete_repair",
#             payload=payload,
#         ),
#         current_user.id,
#     )


# @router.post(
#     "/{asset_id}/repair/{repair_id}/cancel",
#     response_model=RepairSchema,
#     dependencies=[presets.CanUpdateAssets],
# )
# @invalidate_cache(tags=("assets:list",))
# async def cancel_asset_repair(
#     asset_id: UUID,
#     repair_id: UUID,
#     data: RepairCancelRequest,
#     actor: CurrentUserSchema = Depends(get_current_user),
#     service: RepairService = Depends(get_repair_service),
# ):
#     return await service.cancel_repair(asset_id, repair_id, data, actor)


# @router.post(
#     "/{asset_id}/warehouse",
#     response_model=AssetDetailSchema,
#     dependencies=[presets.CanUpdateAssets],
# )
# @invalidate_cache(tags=("assets:list",))
# async def move_asset_to_warehouse(
#     asset_id: UUID,
#     data: WarehouseMoveRequest,
#     actor: CurrentUserSchema = Depends(get_current_user),
#     service: WarehouseService = Depends(get_warehouse_service),
#     asset_service: AssetService = Depends(get_asset_service),
# ):
#     await service.move_asset_to_warehouse(asset_id, data, actor)
#     return await asset_service.get(asset_id, actor)


