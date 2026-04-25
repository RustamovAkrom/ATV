from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from api.dependencies.assets import (
    get_asset_assignment_service,
    get_asset_service,
    get_asset_transfer_service,
    get_bulk_asset_service,
    get_document_service,
    get_export_service,
    get_repair_service,
    get_warehouse_service,
)
from core.cache.decorators import cached, invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
from db.models.enums import AssetStatus
from schemas.asset_assignments import AssetAssignmentRequest, AssetReassignmentRequest
from schemas.asset_transfers import (
    AssetTransferCreate,
    AssetTransferDecision,
    AssetTransferSchema,
)
from schemas.assets import (
    AssetCreate,
    AssetDetailSchema,
    AssetFilters,
    AssetHistorySchema,
    AssetPage,
    AssetStatusChangeRequest,
    AssetUpdate,
)
from schemas.auth import CurrentUserSchema
from schemas.bulk import (
    BulkAssignRequest,
    BulkResult,
    BulkStatusRequest,
    BulkTransferRequest,
)
from schemas.documents import AssetDocumentCreate, AssetDocumentSchema
from schemas.pagination import PaginationParamsSchema
from schemas.repairs import (
    RepairCancelRequest,
    RepairCompleteRequest,
    RepairReportRequest,
    RepairSchema,
    RepairStartRequest,
)
from schemas.warehouses import WarehouseMoveRequest
from services.asset_assignment_service import AssetAssignmentService
from services.asset_service import AssetService
from services.asset_transfer_service import AssetTransferService
from services.bulk_asset_service import BulkAssetService
from services.document_service import DocumentService
from services.export_service import ExportService
from services.repair_service import RepairService
from services.warehouse_service import WarehouseService

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
):
    return await service.list(filters, pagination)


@router.post(
    "/", response_model=AssetDetailSchema, dependencies=[presets.CanCreateAssets]
)
@invalidate_cache(tags=("assets:list",))
async def create_asset(
    data: AssetCreate,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.create(data, current_user.id)


@router.post(
    "/bulk/assign", response_model=BulkResult, dependencies=[presets.CanUpdateAssets]
)
@invalidate_cache(tags=("assets:list",))
async def bulk_assign_assets(
    data: BulkAssignRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_assign(data.asset_ids, data.user_id, current_user.id)


@router.post(
    "/bulk/transfer", response_model=BulkResult, dependencies=[presets.CanUpdateAssets]
)
@invalidate_cache(tags=("assets:list",))
async def bulk_transfer_assets(
    data: BulkTransferRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_transfer(data.asset_ids, data.transfer, current_user.id)


@router.post(
    "/bulk/status", response_model=BulkResult, dependencies=[presets.CanUpdateAssets]
)
@invalidate_cache(tags=("assets:list",))
async def bulk_update_asset_status(
    data: BulkStatusRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: BulkAssetService = Depends(get_bulk_asset_service),
):
    return await service.bulk_update_status(
        data.asset_ids, data.status, current_user.id
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
):
    return await service.get(asset_id)


@router.patch(
    "/{asset_id}",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def update_asset(
    asset_id: UUID,
    data: AssetUpdate,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.update(asset_id, data, current_user.id)


@router.delete("/{asset_id}", dependencies=[presets.CanDeleteAssets])
@invalidate_cache(tags=("assets:list",))
async def delete_asset(
    asset_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    await service.delete(asset_id, current_user.id)
    return {"status": "deleted"}


@router.post(
    "/{asset_id}/assign",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def assign_asset(
    asset_id: UUID,
    data: AssetAssignmentRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
    asset_service: AssetService = Depends(get_asset_service),
):
    await service.assign_asset(asset_id, data.user_id, current_user.id)
    return await asset_service.get(asset_id)


@router.post(
    "/{asset_id}/unassign",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def unassign_asset(
    asset_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
    asset_service: AssetService = Depends(get_asset_service),
):
    await service.unassign_asset(asset_id, current_user.id)
    return await asset_service.get(asset_id)


@router.post(
    "/{asset_id}/reassign",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def reassign_asset(
    asset_id: UUID,
    data: AssetReassignmentRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
    asset_service: AssetService = Depends(get_asset_service),
):
    await service.reassign_asset(asset_id, data.new_user_id, current_user.id)
    return await asset_service.get(asset_id)


@router.post(
    "/{asset_id}/status",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def change_asset_status(
    asset_id: UUID,
    data: AssetStatusChangeRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    return await service.change_status(asset_id, data, current_user.id)


@router.post(
    "/{asset_id}/transfer",
    response_model=AssetTransferSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def create_asset_transfer(
    asset_id: UUID,
    data: AssetTransferCreate,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetTransferService = Depends(get_asset_transfer_service),
):
    return await service.create_transfer(asset_id, data, current_user.id)


@router.post(
    "/{asset_id}/transfer/{transfer_id}/approve",
    response_model=AssetTransferSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def approve_asset_transfer(
    asset_id: UUID,
    transfer_id: UUID,
    data: AssetTransferDecision,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetTransferService = Depends(get_asset_transfer_service),
):
    return await service.approve_transfer(
        asset_id, transfer_id, current_user.id, data.comment
    )


@router.post(
    "/{asset_id}/transfer/{transfer_id}/reject",
    response_model=AssetTransferSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def reject_asset_transfer(
    asset_id: UUID,
    transfer_id: UUID,
    data: AssetTransferDecision,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: AssetTransferService = Depends(get_asset_transfer_service),
):
    return await service.reject_transfer(
        asset_id, transfer_id, current_user.id, data.comment
    )


@router.post(
    "/{asset_id}/repair/report",
    response_model=RepairSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def report_asset_repair(
    asset_id: UUID,
    data: RepairReportRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: RepairService = Depends(get_repair_service),
):
    return await service.report_repair(asset_id, data, current_user.id)


@router.post(
    "/{asset_id}/repair/{repair_id}/start",
    response_model=RepairSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def start_asset_repair(
    asset_id: UUID,
    repair_id: UUID,
    data: RepairStartRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: RepairService = Depends(get_repair_service),
):
    return await service.start_repair(asset_id, repair_id, data, current_user.id)


@router.post(
    "/{asset_id}/repair/{repair_id}/complete",
    response_model=RepairSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def complete_asset_repair(
    asset_id: UUID,
    repair_id: UUID,
    data: RepairCompleteRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: RepairService = Depends(get_repair_service),
):
    return await service.complete_repair(asset_id, repair_id, data, current_user.id)


@router.post(
    "/{asset_id}/repair/{repair_id}/cancel",
    response_model=RepairSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def cancel_asset_repair(
    asset_id: UUID,
    repair_id: UUID,
    data: RepairCancelRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: RepairService = Depends(get_repair_service),
):
    return await service.cancel_repair(asset_id, repair_id, data, current_user.id)


@router.post(
    "/{asset_id}/documents",
    response_model=AssetDocumentSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def attach_asset_document(
    asset_id: UUID,
    data: AssetDocumentCreate,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    return await service.attach_document_to_asset(asset_id, data, current_user.id)


@router.delete(
    "/{asset_id}/documents/{document_id}", dependencies=[presets.CanDeleteAssets]
)
@invalidate_cache(tags=("assets:list",))
async def delete_asset_document(
    asset_id: UUID,
    document_id: UUID,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    await service.delete_document(asset_id, document_id, current_user.id)
    return {"status": "deleted"}


@router.post(
    "/{asset_id}/warehouse",
    response_model=AssetDetailSchema,
    dependencies=[presets.CanUpdateAssets],
)
@invalidate_cache(tags=("assets:list",))
async def move_asset_to_warehouse(
    asset_id: UUID,
    data: WarehouseMoveRequest,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: WarehouseService = Depends(get_warehouse_service),
    asset_service: AssetService = Depends(get_asset_service),
):
    await service.move_asset_to_warehouse(asset_id, data, current_user.id)
    return await asset_service.get(asset_id)


@router.get(
    "/{asset_id}/history",
    response_model=list[AssetHistorySchema],
    dependencies=[presets.CanViewAssets],
)
async def get_asset_history(
    asset_id: UUID,
    service: AssetService = Depends(get_asset_service),
):
    return await service.get_history(asset_id)
