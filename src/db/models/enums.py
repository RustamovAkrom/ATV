from enum import StrEnum


class UserGender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class UserLanguage(StrEnum):
    RU = "ru"
    UZ = "uz"
    EN = "en"


class EmploymentType(StrEnum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACTOR = "contractor"
    INTERN = "intern"


class UserRole(StrEnum):
    OPERATOR = "operator"
    APPROVER = "approver"
    ANALYST = "analyst"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


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
    ACTIVE = "active"
    APPROVED = "approved"


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
