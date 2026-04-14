from enum import Enum


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MODERATOR = "moderator"
    ANALYTIC = "analytic"


class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class AssetStatus(str, Enum):
    ACTIVE = "active"
    IN_STOCK = "in_stock"
    BROKEN = "broken"
    RETIRED = "retired"


class LifecycleStage(str, Enum):
    NEW = "new"
    NORMAL = "normal"
    OLD = "old"
    CRITICAL = "critical"


class RepairStatus(str, Enum):
    REPORTED = "reported"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELED = "canceled"


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class AuditEntity(str, Enum):
    USER = "user"
    ASSET = "asset"
    REPAIR = "repair"
    DOCUMENT = "document"
