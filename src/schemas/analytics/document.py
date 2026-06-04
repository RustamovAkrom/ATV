from schemas.base import BaseResponseSchema


class DocumentAnalyticsDataSchema(BaseResponseSchema):
    total_assets: int
    with_documents: int
    without_documents: int
    missing_compliance_documentation: int
