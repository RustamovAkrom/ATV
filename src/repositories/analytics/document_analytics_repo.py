from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.documents.document import Document
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class DocumentAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики документов"""

    async def metrics(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
        required_document_types: list[str] | None = None,
    ) -> dict:
        """Метрики по документам активов"""
        filters = self.scope_filters(
            Asset, region_id, service_id, scoped_region_id, scoped_service_id
        )

        total = await self.get_count(Asset, filters)

        # Активы с документами
        with_docs = (
            await self.session.scalar(
                select(func.count(func.distinct(Asset.id)))
                .select_from(Asset)
                .join(Document, Document.asset_id == Asset.id)
                .where(*filters)
            )
            or 0
        )

        # Активы без обязательных документов
        missing_compliance = 0
        if required_document_types:
            missing_compliance = (
                await self.session.scalar(
                    select(func.count(Asset.id)).where(
                        *filters,
                        ~Asset.id.in_(
                            select(Document.asset_id).where(
                                Document.document_type.in_(required_document_types)
                            )
                        ),
                    )
                )
                or 0
            )

        return {
            "total_assets": total,
            "with_documents": with_docs,
            "without_documents": max(total - with_docs, 0),
            "missing_compliance_documentation": missing_compliance,
        }
