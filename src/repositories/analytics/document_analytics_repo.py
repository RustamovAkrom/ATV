from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.documents.document import Document
from repositories.base import BaseRepository


class DocumentAnalyticsRepository(BaseRepository):
    @staticmethod
    def _scope_filters(
        region_id: UUID | None,
        service_id: UUID | None,
        scoped_region_id: UUID | None,
        scoped_service_id: UUID | None,
    ):
        filters = []
        if scoped_region_id or region_id:
            filters.append(Asset.region_id == (scoped_region_id or region_id))
        if scoped_service_id or service_id:
            filters.append(Asset.service_id == (scoped_service_id or service_id))
        return filters

    async def metrics(
        self,
        region_id: UUID | None,
        service_id: UUID | None,
        scoped_region_id: UUID | None,
        scoped_service_id: UUID | None,
        required_document_types: list[str],
    ):
        filters = self._scope_filters(
            region_id, service_id, scoped_region_id, scoped_service_id
        )
        total = int(
            (await self.execute(select(func.count(Asset.id)).where(*filters))).scalar_one()
            or 0
        )
        with_docs = int(
            (
                await self.execute(
                    select(func.count(func.distinct(Asset.id)))
                    .select_from(Asset)
                    .join(Document, Document.asset_id == Asset.id)
                    .where(*filters)
                )
            ).scalar_one()
            or 0
        )
        missing_compliance = int(
            (
                await self.execute(
                    select(func.count(Asset.id))
                    .where(
                        *filters,
                        ~Asset.id.in_(
                            select(Document.asset_id).where(
                                Document.document_type.in_(required_document_types)
                            )
                        ),
                    )
                )
            ).scalar_one()
            or 0
        )
        return {
            "total_assets": total,
            "with_documents": with_docs,
            "without_documents": max(total - with_docs, 0),
            "missing_compliance_documentation": missing_compliance,
        }
