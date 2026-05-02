from pydantic import BaseModel


class ApprovalAnalyticsDataSchema(BaseModel):
    pending_approvals: int
    average_approval_time_hours: float
    rejection_rate: float
