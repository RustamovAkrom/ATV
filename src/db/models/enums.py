from enum import StrEnum


class UserRole(StrEnum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    ANALYTIC = "analytic"
    # Extended roles for enterprises
    REGION_ADMIN = "region_admin"
    SERVICE_MANAGER = "service_manager"
    OPERATOR = "operator"
    APPROVER = "approver"
    AUDITOR = "auditor"


class UserStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class AssetStatus(StrEnum):
    ACTIVE = "active"
    ASSIGNED = "assigned"
    IN_REPAIR = "in_repair"
    ARCHIVED = "archived"


class TransferStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LifecycleStage(StrEnum):
    NEW = "new"
    NORMAL = "normal"
    OLD = "old"
    CRITICAL = "critical"


class RepairStatus(StrEnum):
    REPORTED = "reported"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


class DocumentStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditEntity(StrEnum):
    USER = "user"
    ASSET = "asset"
    REPAIR = "repair"
    DOCUMENT = "document"
