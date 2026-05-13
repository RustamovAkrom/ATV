from schemas.base import BaseSchema

class ApprovalAnalyticsDataSchema(BaseSchema):
    pending_approvals: int
    average_approval_time_hours: float
    rejection_rate: float
