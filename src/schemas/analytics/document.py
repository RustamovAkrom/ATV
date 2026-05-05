from pydantic import BaseModel


class DocumentAnalyticsDataSchema(BaseModel):
    total_assets: int
    with_documents: int
    without_documents: int
    missing_compliance_documentation: int
