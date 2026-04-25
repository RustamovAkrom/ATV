import pytest
from types import SimpleNamespace
from uuid import uuid4

from core.security.auth.types import CurrentUser
from db.models.enums import UserRole
from schemas.analytics.top import TopMetric
from services.analytics.top_analytics_service import TopAnalyticsService

pytestmark = pytest.mark.anyio


class _Repo:
    async def get_top_users(self, limit: int):
        return [
            SimpleNamespace(
                id=uuid4(),
                full_name="Analytic User",
                email="analytic@test.local",
                assignment_count=3,
                transfer_count=1,
                repair_count=0,
            )
        ]


async def test_top_users_masks_email_for_non_admin():
    service = TopAnalyticsService(_Repo())
    current_user = CurrentUser(id=uuid4(), role=UserRole.ANALYTIC.value, permissions=["assets.view"])

    result = await service.get_top_users(TopMetric.ASSIGNMENTS, 5, current_user)

    assert result[0].email == ""


async def test_top_users_keeps_email_for_admin():
    service = TopAnalyticsService(_Repo())
    current_user = CurrentUser(id=uuid4(), role=UserRole.ADMIN.value, permissions=["assets.view"])

    result = await service.get_top_users(TopMetric.ASSIGNMENTS, 5, current_user)

    assert result[0].email == "analytic@test.local"
