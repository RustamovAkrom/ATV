import pytest

from schemas.audit import AuditCreateSchema, AuditFiltersSchema
from schemas.pagination import PaginationParamsSchema
from services.audit_service import AuditService


@pytest.fixture
def sample_payload():
    return AuditCreateSchema(
        method="GET",
        path="/test",
        status_code=200,
        user_id=None,
        request_id="req-1",
        latency_ms=10,
        ip="127.0.0.1",
        user_agent="pytest",
        is_suspicious=False,
        query=None,
    )


@pytest.mark.anyio
async def test_create_audit_log(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    result = await service.persist_audit(sample_payload)

    assert result.id is not None
    assert result.method == "GET"
    assert result.path == "/test"
    assert result.request_id == "req-1"


@pytest.mark.anyio
async def test_list_audit_logs_empty(dbsession):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    page = await service.list_audit_logs(
        filters=AuditFiltersSchema(),
        pagination=PaginationParamsSchema(page=1, limit=10),
    )

    assert page.total == 0
    assert page.items == []


@pytest.mark.anyio
async def test_list_audit_logs_with_data(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    await service.persist_audit(sample_payload)

    page = await service.list_audit_logs(
        filters=AuditFiltersSchema(),
        pagination=PaginationParamsSchema(page=1, limit=10),
    )

    assert page.total == 1
    assert len(page.items) == 1
    assert page.items[0].request_id == "req-1"


@pytest.mark.anyio
async def test_filter_by_user_id(
    dbsession, sample_payload, create_user
):  # Добавили фикстуру create_user
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    # 1. Создаем РЕАЛЬНОГО пользователя в базе данных
    user = await create_user(login="audit_test_user")
    user_id = user.id  # Это настоящий UUID, который есть в таблице users

    # 2. Теперь база пропустит этот INSERT, так как FK будет валидным
    await service.persist_audit(sample_payload.model_copy(update={"user_id": user_id}))

    page = await service.list_audit_logs(
        filters=AuditFiltersSchema(user_id=user_id),
        pagination=PaginationParamsSchema(page=1, limit=10),
    )

    assert page.total == 1
    # Сравниваем UUID объекты
    assert page.items[0].user_id == user_id


@pytest.mark.anyio
async def test_filter_by_status_code(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    await service.persist_audit(sample_payload.model_copy(update={"status_code": 500}))

    page = await service.list_audit_logs(
        filters=AuditFiltersSchema(status_code=500),
        pagination=PaginationParamsSchema(page=1, limit=10),
    )

    assert page.total == 1
    assert page.items[0].status_code == 500


@pytest.mark.anyio
async def test_filter_by_search(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    await service.persist_audit(
        sample_payload.model_copy(update={"path": "/search/test"})
    )

    page = await service.list_audit_logs(
        filters=AuditFiltersSchema(search="search"),
        pagination=PaginationParamsSchema(page=1, limit=10),
    )

    assert page.total == 1
    assert "search" in page.items[0].path


@pytest.mark.anyio
async def test_get_by_request_id(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    await service.persist_audit(sample_payload)

    page = await service.get_by_request_id(
        request_id="req-1",
        pagination=PaginationParamsSchema(page=1, limit=10),
    )

    assert page.total == 1
    assert page.items[0].request_id == "req-1"


@pytest.mark.anyio
async def test_get_errors(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    await service.persist_audit(sample_payload.model_copy(update={"status_code": 500}))

    page = await service.get_errors(
        pagination=PaginationParamsSchema(page=1, limit=10),
    )

    assert page.total == 1
    assert page.items[0].status_code >= 400


@pytest.mark.anyio
async def test_get_stats(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    await service.persist_audit(sample_payload)
    await service.persist_audit(sample_payload.model_copy(update={"status_code": 500}))
    await service.persist_audit(
        sample_payload.model_copy(update={"is_suspicious": True})
    )

    stats = await service.get_stats()

    assert stats.total == 3
    assert stats.errors >= 1
    assert stats.server_errors >= 1
    assert stats.suspicious >= 1


@pytest.mark.anyio
async def test_pagination(dbsession, sample_payload):
    from repositories.audit_repo import AuditRepository

    service = AuditService(AuditRepository(dbsession))

    for i in range(5):
        await service.persist_audit(
            sample_payload.model_copy(update={"request_id": f"req-{i}"})
        )

    page = await service.list_audit_logs(
        filters=AuditFiltersSchema(),
        pagination=PaginationParamsSchema(page=1, limit=2),
    )

    assert page.total == 5
    assert len(page.items) == 2
