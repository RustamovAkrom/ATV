from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.exceptions.errors import BadRequest, NotFound
from db.models.enums import AssetStatus, UserStatus
from schemas.assets.assets import (
    AssetCreate,
    AssetFilters,
    AssetHistorySchema,
    AssetStatusChangeRequest,
    AssetUpdate,
)
from schemas.auth.auth import CurrentUserSchema
from schemas.pagination import PaginationParamsSchema
from services.assets.asset_service import AssetService

pytestmark = pytest.mark.anyio


class _FakeEvents:
    async def created(self, **kwargs):
        return None

    async def updated(self, **kwargs):
        return None

    async def status_changed(self, **kwargs):
        return None

    async def deleted(self, **kwargs):
        return None


class _FakeRepo:
    def __init__(self):
        self.asset_id = uuid4()
        self.region_id = uuid4()
        self.service_id = uuid4()
        self.owner_id = uuid4()
        self.asset = SimpleNamespace(
            id=self.asset_id,
            name="Asset",
            model_id=uuid4(),
            class_id=uuid4(),
            region_id=self.region_id,
            service_id=self.service_id,
            owner_id=None,
            status=AssetStatus.ACTIVE,
            serial_number="SN-1",
            meta={},
            history_entries=[],
            assignments=[],
        )

    async def list(self, filters, pagination):
        return [self.asset], 1

    async def get_by_id(self, asset_id, include_history=True):
        return self.asset if asset_id == self.asset_id else None

    async def get_by_id_for_update(self, asset_id, include_history=True):
        return await self.get_by_id(asset_id, include_history)

    async def get_user(self, user_id):
        return SimpleNamespace(
            id=user_id,
            region_id=self.region_id,
            service_id=self.service_id,
            status=UserStatus.ACTIVE.value,
        )

    async def get_model(self, model_id):
        return SimpleNamespace(id=model_id)

    async def get_region(self, region_id):
        return SimpleNamespace(id=region_id)

    async def get_service(self, service_id):
        return SimpleNamespace(id=service_id)

    async def get_asset_class(self, class_id):
        return SimpleNamespace(id=class_id)

    async def serial_number_exists(self, serial_number, exclude_id=None):
        return False

    async def create(self, asset):
        asset.id = self.asset_id
        asset.region_id = self.region_id
        asset.service_id = self.service_id
        asset.status = asset.status
        asset.owner_id = asset.owner_id
        self.asset = asset

    async def flush(self):
        return None

    async def delete(self, asset):
        self.asset = None


@pytest.fixture
def actor():
    return CurrentUserSchema(id=uuid4(), role="superadmin", permissions=[])


@pytest.fixture
def asset_service(monkeypatch):
    import services.assets.asset_service as module

    monkeypatch.setattr(
        module.AccessControl, "check_region_access", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        module.AccessControl, "check_service_access", lambda *args, **kwargs: None
    )

    repo = _FakeRepo()
    service = AssetService(repo, _FakeEvents())
    return service, repo


class TestAssetService:
    async def test_list_and_history_paths(self, asset_service, actor):
        service, repo = asset_service

        repo.asset.history_entries = [
            SimpleNamespace(
                id=uuid4(),
                action="created",
                details={},
                created_at=datetime.now(UTC),
                user_id=None,
                user=None,
            )
        ]

        actor.assigned_region_id = repo.region_id
        actor.assigned_service_id = repo.service_id

        page = await service.list(
            AssetFilters(), PaginationParamsSchema(page=1, limit=10), actor
        )
        assert page.total == 1
        assert len(page.items) == 1

        history = await service.get_history(repo.asset_id, actor)
        assert isinstance(history, list)
        assert isinstance(history[0], AssetHistorySchema)

    async def test_create_update_change_status_delete(
        self, asset_service, actor, monkeypatch
    ):
        service, repo = asset_service

        async def _fake_get(asset_id, actor):
            return SimpleNamespace(id=asset_id)

        monkeypatch.setattr(service, "get", _fake_get)

        create_payload = AssetCreate(
            name="Asset 1",
            model_id=uuid4(),
            class_id=uuid4(),
            region_id=repo.region_id,
            service_id=repo.service_id,
            serial_number="SN-2",
        )
        created = await service.create(create_payload, actor)
        assert created.id == repo.asset_id

        update_payload = AssetUpdate(name="Updated")
        updated = await service.update(repo.asset_id, update_payload, actor)
        assert updated.id == repo.asset_id

        repo.asset.status = AssetStatus.ACTIVE
        status_payload = AssetStatusChangeRequest(status=AssetStatus.IN_REPAIR)
        changed = await service.change_status(repo.asset_id, status_payload, actor)
        assert changed.id == repo.asset_id

        repo.asset.status = AssetStatus.ARCHIVED
        await service.delete(repo.asset_id, actor)

    async def test_not_found_and_invalid_transitions(self, asset_service, actor):
        service, repo = asset_service

        with pytest.raises(NotFound):
            await service.get(uuid4(), actor)

        repo.asset.status = AssetStatus.ASSIGNED
        repo.asset.owner_id = None
        # ASSIGNED -> ACTIVE is allowed only when owner is cleared (owner_id is None).
        service._validate_status_change(repo.asset, AssetStatus.ACTIVE)

        repo.asset.owner_id = uuid4()
        with pytest.raises(BadRequest):
            service._validate_status_change(repo.asset, AssetStatus.ACTIVE)

    async def test_validate_uniques_and_clean_optional(
        self, asset_service, actor, monkeypatch
    ):
        service, repo = asset_service

        async def _serial_exists(*args, **kwargs):
            return True

        repo.serial_number_exists = _serial_exists

        with pytest.raises(BadRequest):
            await service._validate_uniques("SN-EXISTS", None)

        assert service._clean_optional("  ") is None
        assert service._clean_optional("  x ") == "x"

    async def test_delete_active_asset_forbidden(self, asset_service, actor):
        service, repo = asset_service
        repo.asset.status = AssetStatus.ACTIVE

        with pytest.raises(BadRequest):
            await service.delete(repo.asset_id, actor)

    async def test_update_and_change_status_noop_return_current(
        self, asset_service, actor, monkeypatch
    ):
        service, repo = asset_service

        async def _fake_get(asset_id, actor):
            return SimpleNamespace(id=asset_id, marker="same")

        monkeypatch.setattr(service, "get", _fake_get)

        result = await service.update(repo.asset_id, AssetUpdate(), actor)
        assert result.marker == "same"

        same_status = AssetStatusChangeRequest(status=repo.asset.status)
        result = await service.change_status(repo.asset_id, same_status, actor)
        assert result.marker == "same"

    async def test_reference_validation_errors(self, asset_service):
        service, repo = asset_service

        async def _none(*args, **kwargs):
            return None

        async def _ok(*args, **kwargs):
            return SimpleNamespace(id=uuid4())

        # model missing
        repo.get_model = _none
        with pytest.raises(BadRequest):
            await service._validate_references(
                uuid4(), repo.region_id, repo.service_id, None, repo.asset.class_id
            )

        # region missing
        repo.get_model = _ok
        repo.get_region = _none
        with pytest.raises(BadRequest):
            await service._validate_references(
                uuid4(), repo.region_id, repo.service_id, None, repo.asset.class_id
            )

        # service missing
        repo.get_region = _ok
        repo.get_service = _none
        with pytest.raises(BadRequest):
            await service._validate_references(
                uuid4(), repo.region_id, repo.service_id, None, repo.asset.class_id
            )

        # class missing
        repo.get_service = _ok
        repo.get_asset_class = _none
        with pytest.raises(BadRequest):
            await service._validate_references(
                uuid4(), repo.region_id, repo.service_id, None, repo.asset.class_id
            )

        # owner inactive
        repo.get_asset_class = _ok

        async def _blocked_user(*args, **kwargs):
            return SimpleNamespace(id=uuid4(), status=UserStatus.BLOCKED.value)

        repo.get_user = _blocked_user
        with pytest.raises(BadRequest):
            await service._validate_references(
                uuid4(),
                repo.region_id,
                repo.service_id,
                repo.owner_id,
                repo.asset.class_id,
            )

    async def test_validate_update_references_errors(self, asset_service):
        service, repo = asset_service

        async def _none(*args, **kwargs):
            return None

        async def _ok(*args, **kwargs):
            return SimpleNamespace(id=uuid4())

        repo.get_model = _none
        with pytest.raises(BadRequest):
            await service._validate_update_references({"model_id": uuid4()})

        repo.get_model = _ok
        repo.get_region = _none
        with pytest.raises(BadRequest):
            await service._validate_update_references({"region_id": uuid4()})

        repo.get_region = _ok
        repo.get_service = _none
        with pytest.raises(BadRequest):
            await service._validate_update_references({"service_id": uuid4()})

        repo.get_service = _ok
        repo.get_asset_class = _none
        with pytest.raises(BadRequest):
            await service._validate_update_references({"class_id": uuid4()})
