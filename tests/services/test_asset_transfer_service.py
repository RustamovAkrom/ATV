from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.exceptions.errors import BadRequest, NotFound
from db.models.enums import AssetStatus, TransferStatus
from schemas.assets.asset_transfers import AssetTransferCreate
from schemas.auth.auth import CurrentUserSchema
from services.assets.asset_transfer_service import AssetTransferService

pytestmark = pytest.mark.anyio


class _FakeEvents:
    async def created(self, **kwargs):
        return None

    async def approved(self, **kwargs):
        return None

    async def rejected(self, **kwargs):
        return None


class _FakeRepo:
    def __init__(self):
        self.asset_id = uuid4()
        self.region_id = uuid4()
        self.service_id = uuid4()
        self.warehouse_id = uuid4()
        self.transfer_id = uuid4()

        self.asset = SimpleNamespace(
            id=self.asset_id,
            region_id=self.region_id,
            service_id=self.service_id,
            current_warehouse_id=self.warehouse_id,
            status=AssetStatus.ACTIVE,
            is_transfer_locked=False,
        )
        self.transfer = SimpleNamespace(
            id=self.transfer_id,
            asset_id=self.asset_id,
            created_by_id=uuid4(),
            received_by_id=None,
            status=TransferStatus.PENDING,
            from_warehouse_id=self.warehouse_id,
            to_warehouse_id=self.warehouse_id,
            from_service_id=self.service_id,
            to_service_id=None,
            comment=None,
            transferred_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

    async def get_asset_for_update(self, asset_id):
        return self.asset if asset_id == self.asset_id else None

    async def get_active_assignments(self, asset_id):
        return []

    async def get_pending_transfer(self, asset_id):
        return None

    async def get_warehouse(self, warehouse_id):
        return SimpleNamespace(
            id=warehouse_id, region_id=self.region_id, service_id=self.service_id
        )

    async def get_service(self, service_id):
        return SimpleNamespace(id=service_id)

    async def create_transfer(self, transfer):
        transfer.id = uuid4()
        transfer.transferred_at = datetime.now(UTC)
        transfer.created_at = datetime.now(UTC)
        transfer.updated_at = datetime.now(UTC)
        transfer.status = TransferStatus.PENDING
        self.transfer = transfer

    async def flush(self):
        return None

    async def get_transfer_for_update(self, transfer_id):
        return self.transfer if transfer_id == self.transfer.id else None


@pytest.fixture
def actor():
    return CurrentUserSchema(
        id=uuid4(),
        role="superadmin",
        permissions=[],
        assigned_region_id=None,
        assigned_service_id=None,
    )


@pytest.fixture
def transfer_service(monkeypatch):
    import services.assets.asset_transfer_service as module

    # bypass permission checks for unit isolation
    monkeypatch.setattr(
        module.AccessControl, "check_region_access", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        module.AccessControl, "check_service_access", lambda *args, **kwargs: None
    )

    repo = _FakeRepo()
    service = AssetTransferService(repo, _FakeEvents())
    return service, repo


class TestAssetTransferService:
    async def test_create_transfer_success(self, transfer_service, actor):
        service, repo = transfer_service
        payload = AssetTransferCreate(to_warehouse_id=repo.warehouse_id, comment="Test")

        result = await service.create_transfer(repo.asset_id, payload, actor)
        assert result.asset_id == repo.asset_id
        assert result.status == TransferStatus.PENDING

    async def test_create_transfer_locked_asset(self, transfer_service, actor):
        service, repo = transfer_service
        repo.asset.is_transfer_locked = True
        payload = AssetTransferCreate(to_warehouse_id=repo.warehouse_id)

        with pytest.raises(BadRequest):
            await service.create_transfer(repo.asset_id, payload, actor)

    async def test_create_transfer_asset_not_found(self, transfer_service, actor):
        service, repo = transfer_service
        payload = AssetTransferCreate(to_warehouse_id=repo.warehouse_id)

        with pytest.raises(NotFound):
            await service.create_transfer(uuid4(), payload, actor)

    async def test_approve_transfer_success(self, transfer_service, actor):
        service, repo = transfer_service
        payload = AssetTransferCreate(to_warehouse_id=repo.warehouse_id)
        created = await service.create_transfer(repo.asset_id, payload, actor)

        result = await service.approve_transfer(
            repo.asset_id, created.id, actor, comment="ok"
        )
        assert result.status == TransferStatus.COMPLETED

    async def test_approve_transfer_already_completed(self, transfer_service, actor):
        service, repo = transfer_service
        repo.transfer.status = TransferStatus.COMPLETED

        with pytest.raises(BadRequest):
            await service.approve_transfer(repo.asset_id, repo.transfer.id, actor)

    async def test_reject_transfer_success(self, transfer_service, actor):
        service, repo = transfer_service
        payload = AssetTransferCreate(to_warehouse_id=repo.warehouse_id)
        created = await service.create_transfer(repo.asset_id, payload, actor)

        result = await service.reject_transfer(
            repo.asset_id, created.id, actor, comment="no"
        )
        assert result.status == TransferStatus.CANCELLED

    async def test_reject_transfer_not_found(self, transfer_service, actor):
        service, repo = transfer_service
        with pytest.raises(NotFound):
            await service.reject_transfer(repo.asset_id, uuid4(), actor)
