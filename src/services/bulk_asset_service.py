from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.base import APIException
from core.exceptions.errors import BadRequest
from schemas.asset_transfers import AssetTransferCreate
from schemas.assets import AssetStatusChangeRequest
from schemas.bulk import BulkFailedItem, BulkResult


class BulkAssetService:
    MAX_BATCH_SIZE = 100

    def __init__(self, session: AsyncSession, assignment_service, transfer_service, asset_service):
        self.session = session
        self.assignment_service = assignment_service
        self.transfer_service = transfer_service
        self.asset_service = asset_service

    async def bulk_assign(self, asset_ids, user_id, actor_id) -> BulkResult:
        asset_ids = self._validate_asset_ids(asset_ids)
        return await self._process_items(
            asset_ids,
            lambda asset_id: self.assignment_service.assign_asset(asset_id, user_id, actor_id),
        )

    async def bulk_transfer(self, asset_ids, transfer: AssetTransferCreate, actor_id) -> BulkResult:
        asset_ids = self._validate_asset_ids(asset_ids)
        return await self._process_items(
            asset_ids,
            lambda asset_id: self.transfer_service.create_transfer(asset_id, transfer, actor_id),
        )

    async def bulk_update_status(self, asset_ids, status, actor_id) -> BulkResult:
        asset_ids = self._validate_asset_ids(asset_ids)
        return await self._process_items(
            asset_ids,
            lambda asset_id: self.asset_service.change_status(
                asset_id,
                AssetStatusChangeRequest(status=status),
                actor_id,
            ),
        )

    async def _process_items(self, asset_ids, callback) -> BulkResult:
        success = []
        failed = []
        for asset_id in asset_ids:
            try:
                async with self.session.begin_nested():
                    await callback(asset_id)
                success.append(asset_id)
            except APIException as exc:
                failed.append(BulkFailedItem(id=asset_id, error=str(exc.detail)))
            except Exception as exc:
                failed.append(BulkFailedItem(id=asset_id, error=str(exc)))
        return BulkResult(success=success, failed=failed)

    def _validate_asset_ids(self, asset_ids):
        if not asset_ids:
            raise BadRequest("asset_ids must not be empty")
        if len(asset_ids) > self.MAX_BATCH_SIZE:
            raise BadRequest(f"Maximum batch size is {self.MAX_BATCH_SIZE}")
        if len(set(asset_ids)) != len(asset_ids):
            raise BadRequest("asset_ids must be unique")
        return asset_ids
