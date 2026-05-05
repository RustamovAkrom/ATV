from repositories.analytics.document_analytics_repo import DocumentAnalyticsRepository
from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from services.analytics._scope import validate_filters


class DocumentAnalyticsDomainService:
    REQUIRED_COMPLIANCE_DOCUMENT_TYPES = [
        "passport",
        "warranty",
        "commissioning_act",
    ]

    def __init__(self, repo: DocumentAnalyticsRepository):
        self.repo = repo

    async def get(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        validate_filters(filters, user)
        return await self.repo.metrics(
            filters.region_id,
            filters.service_id,
            user.assigned_region_id,
            user.assigned_service_id,
            self.REQUIRED_COMPLIANCE_DOCUMENT_TYPES,
        )
