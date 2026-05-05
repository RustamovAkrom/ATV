from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.documents.document import get_document_service
from core.cache.decorators import invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions

from schemas.auth import CurrentUserSchema
from schemas.documents import AssetDocumentCreate, AssetDocumentSchema
from schemas.common import StatusResponse

from services.documents.document_service import DocumentService


router = APIRouter(
    prefix="/assets/{asset_id}/documents",
    tags=["Asset Documents"],
)


@router.get("/", response_model=list[AssetDocumentSchema], dependencies=[Depends(AssetPermissions.CanViewAssets)])
async def list_documents(
    asset_id: UUID,
    service: DocumentService = Depends(get_document_service),
    actor: CurrentUserSchema = Depends(get_current_user),
):
    return await service.list_by_asset(asset_id, actor)


@router.post(
    "/",
    response_model=AssetDocumentSchema,
    dependencies=[Depends(AssetPermissions.CanUpdateAssets)],
)
@invalidate_cache(tags=("assets:list",))
async def attach_asset_document(
    asset_id: UUID,
    data: AssetDocumentCreate,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    return await service.attach_document_to_asset(asset_id, data, actor)


@router.delete(
    "/{document_id}",
    dependencies=[Depends(AssetPermissions.CanDeleteAssets)],
)
@invalidate_cache(tags=("assets:list",))
async def delete_asset_document(
    asset_id: UUID,
    document_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    await service.delete_document(asset_id, document_id, actor)
    return StatusResponse(status="deleted", message="Asset document successfully deleated")
