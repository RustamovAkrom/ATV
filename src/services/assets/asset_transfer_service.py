from uuid import UUID

from core.audit.stream import audit_stream
from core.exceptions.errors import BadRequest, NotFound
from db.models.assets.asset_transfer import AssetTransfer
from db.models.enums import TransferStatus
from repositories.assets.asset_transfer_repo import AssetTransferRepository
from schemas.assets.asset_transfers import AssetTransferCreate, AssetTransferSchema
from utils.helpers import utc_now
from schemas.auth.auth import CurrentUserSchema

class AssetTransferService:
    def __init__(self, repo: AssetTransferRepository):
        self.repo = repo

    async def create_transfer(
        self,
        asset_id: UUID,
        data: AssetTransferCreate,
        actor: CurrentUserSchema,
    ) -> AssetTransferSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")
        if asset.is_transfer_locked:
            raise BadRequest("Asset transfer is locked")

        to_warehouse = None
        if data.to_warehouse_id is not None:
            to_warehouse = await self.repo.get_warehouse(data.to_warehouse_id)
            if not to_warehouse:
                raise BadRequest("Invalid target warehouse")
        if data.to_service_id is not None and not await self.repo.get_service(
            data.to_service_id
        ):
            raise BadRequest("Invalid target service")
        if data.to_warehouse_id is None and data.to_service_id is None:
            raise BadRequest("Transfer requires a target warehouse or service")

        transfer = AssetTransfer(
            asset_id=asset.id,
            created_by_id=actor.id,
            status=TransferStatus.PENDING,
            from_warehouse_id=asset.current_warehouse_id,
            to_warehouse_id=data.to_warehouse_id,
            from_service_id=asset.service_id,
            to_service_id=data.to_service_id,
            comment=(data.comment or "").strip() or None,
        )
        await self.repo.create_transfer(transfer)
        await self.repo.add_history(
            asset.id, actor.id, "transfer_created", f"Transfer {transfer.id} created"
        )
        await self._publish(
            "asset.transfer_created",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor.id),
                "transfer_id": str(transfer.id),
            },
        )
        return AssetTransferSchema.model_validate(transfer, from_attributes=True)

    async def approve_transfer(
        self,
        asset_id: UUID,
        transfer_id: UUID,
        actor: CurrentUserSchema,
        comment: str | None = None,
    ) -> AssetTransferSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        transfer = await self.repo.get_transfer_for_update(transfer_id)
        if not transfer or transfer.asset_id != asset.id:
            raise NotFound("Transfer not found")
        if transfer.status != TransferStatus.PENDING:
            raise BadRequest("Only pending transfers can be approved")

        if transfer.to_warehouse_id is not None:
            warehouse = await self.repo.get_warehouse(transfer.to_warehouse_id)
            if not warehouse:
                raise BadRequest("Invalid target warehouse")
            asset.current_warehouse_id = warehouse.id
            asset.region_id = warehouse.region_id
            if warehouse.service_id is not None:
                asset.service_id = warehouse.service_id
        if transfer.to_service_id is not None:
            service = await self.repo.get_service(transfer.to_service_id)
            if not service:
                raise BadRequest("Invalid target service")
            asset.service_id = service.id

        transfer.status = TransferStatus.COMPLETED
        transfer.received_by_id = actor.id
        if comment is not None:
            transfer.comment = comment.strip() or None
        await self.repo.flush()

        await self.repo.add_history(
            asset.id, actor.id, "transfer_approved", f"Transfer {transfer.id} approved"
        )
        await self._publish(
            "asset.transfer_approved",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor.id),
                "transfer_id": str(transfer.id),
            },
        )
        return AssetTransferSchema.model_validate(transfer, from_attributes=True)

    async def reject_transfer(
        self,
        asset_id: UUID,
        transfer_id: UUID,
        actor: CurrentUserSchema,
        comment: str | None = None,
    ) -> AssetTransferSchema:
        asset = await self.repo.get_asset_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        transfer = await self.repo.get_transfer_for_update(transfer_id)
        if not transfer or transfer.asset_id != asset.id:
            raise NotFound("Transfer not found")
        if transfer.status != TransferStatus.PENDING:
            raise BadRequest("Only pending transfers can be rejected")

        transfer.status = TransferStatus.CANCELLED
        transfer.received_by_id = actor.id
        if comment is not None:
            transfer.comment = comment.strip() or None
        await self.repo.flush()

        await self.repo.add_history(
            asset.id, actor.id, "transfer_rejected", f"Transfer {transfer.id} rejected"
        )
        await self._publish(
            "asset.transfer_rejected",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor.id),
                "transfer_id": str(transfer.id),
            },
        )
        return AssetTransferSchema.model_validate(transfer, from_attributes=True)

    async def _publish(self, event: str, payload: dict) -> None:
        try:
            await audit_stream.publish(
                {"event": event, **payload, "timestamp": utc_now().timestamp()}
            )
        except Exception:
            return
