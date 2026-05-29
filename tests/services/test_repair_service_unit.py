from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import pytest

from core.exceptions.errors import BadRequest, NotFound
from db.models.enums import AssetStatus, RepairStatus, UserStatus
from schemas.assets.repairs import (
    RepairCancelRequest,
    RepairCompleteRequest,
    RepairReportRequest,
    RepairStartRequest,
)
from schemas.auth.auth import CurrentUserSchema
from services.assets.repair_service import RepairService

pytestmark = pytest.mark.anyio


class _FakeEvents:
    async def reported(self, **kwargs):
        return None

    async def started(self, **kwargs):
        return None

    async def completed(self, **kwargs):
        return None

    async def canceled(self, **kwargs):
        return None


class _FakeRepo:
    def __init__(self):
        self.asset_id = uuid4()
        self.repair_id = uuid4()
        self.region_id = uuid4()
        self.service_id = uuid4()

        self.asset = SimpleNamespace(
            id=self.asset_id,
            region_id=self.region_id,
            service_id=self.service_id,
            status=AssetStatus.ACTIVE,
            last_repair_date=None,
            failure_count=0,
        )
        self.repair = SimpleNamespace(
            id=self.repair_id,
            asset_id=self.asset_id,
            reported_by_id=uuid4(),
            assigned_to_id=None,
            description=None,
            status=RepairStatus.REPORTED,
            started_at=None,
            completed_at=None,
            labor_cost=Decimal("0"),
            parts=[],
        )

    async def get_asset_for_update(self, asset_id):
        return self.asset if asset_id == self.asset_id else None

    async def get_active_assignment(self, asset_id):
        return None

    async def get_active_repair(self, asset_id):
        return None

    async def create_repair(self, repair):
        repair.id = self.repair_id
        repair.parts = []
        self.repair = repair

    async def get_repair_for_update(self, repair_id):
        return self.repair if repair_id == self.repair_id else None

    async def get_user(self, user_id):
        return SimpleNamespace(id=user_id, status=UserStatus.ACTIVE.value)

    async def replace_parts(self, repair, parts):
        repair.parts = parts

    async def flush(self):
        return None


@pytest.fixture
def actor():
    return CurrentUserSchema(id=uuid4(), role="superadmin", permissions=[])


@pytest.fixture
def repair_service(monkeypatch):
    import services.assets.repair_service as module

    monkeypatch.setattr(
        module.AccessControl, "check_region_access", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(
        module.AccessControl, "check_service_access", lambda *args, **kwargs: None
    )

    repo = _FakeRepo()
    service = RepairService(repo, _FakeEvents())
    return service, repo


class TestRepairService:
    async def test_report_start_complete_cancel_flow(self, repair_service, actor):
        service, repo = repair_service

        reported = await service.report_repair(
            repo.asset_id, RepairReportRequest(description="Issue"), actor
        )
        assert reported.status == RepairStatus.REPORTED

        started = await service.start_repair(
            repo.asset_id,
            repo.repair_id,
            RepairStartRequest(description="Start", labor_cost=Decimal("10")),
            actor,
        )
        assert started.status == RepairStatus.IN_PROGRESS

        completed = await service.complete_repair(
            repo.asset_id,
            repo.repair_id,
            RepairCompleteRequest(labor_cost=Decimal("20")),
            actor,
        )
        assert completed.status == RepairStatus.DONE

        repo.repair.status = RepairStatus.REPORTED
        canceled = await service.cancel_repair(
            repo.asset_id,
            repo.repair_id,
            RepairCancelRequest(reason="No parts"),
            actor,
        )
        assert canceled.status == RepairStatus.CANCELED

    async def test_error_paths(self, repair_service, actor):
        service, repo = repair_service

        with pytest.raises(NotFound):
            await service.report_repair(
                uuid4(), RepairReportRequest(description="x"), actor
            )

        repo.asset.status = AssetStatus.ASSIGNED
        with pytest.raises(BadRequest):
            await service.report_repair(
                repo.asset_id, RepairReportRequest(description="x"), actor
            )

        repo.asset.status = AssetStatus.ACTIVE
        repo.repair.status = RepairStatus.DONE
        with pytest.raises(BadRequest):
            await service.start_repair(
                repo.asset_id, repo.repair_id, RepairStartRequest(), actor
            )

        repo.repair.status = RepairStatus.REPORTED
        with pytest.raises(BadRequest):
            await service.complete_repair(
                repo.asset_id, repo.repair_id, RepairCompleteRequest(), actor
            )

        repo.repair.status = RepairStatus.DONE
        with pytest.raises(BadRequest):
            await service.cancel_repair(
                repo.asset_id, repo.repair_id, RepairCancelRequest(reason="x"), actor
            )
