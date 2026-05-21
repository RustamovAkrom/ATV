from core.admin.base import BaseAdmin
from db.models.audit.audit_log import AuditLog
from db.models.notifications.notification import Notification
from db.models.refresh_token import RefreshToken
from db.models.system.system_config import SystemConfig


class AuditLogAdmin(BaseAdmin, model=AuditLog):
    name = "Audit Log"
    name_plural = "Audit Logs"
    icon = "fa-solid fa-eye"

    column_list = [
        "id",
        "method",
        "path",
        "status_code",
        "latency_ms",
        "ip",
        "user_agent",
        "created_at",
    ]

    column_sortable_list = [
        "created_at",
        "latency_ms",
    ]



class NotificationAdmin(BaseAdmin, model=Notification):
    name = "Notification"
    name_plural = "Notifications"
    icon = "fa-solid fa-bell"

    column_list = [
        "id",
        "user",
        "type",
        "title",
        "message",
        "is_read",
        "created_at",
    ]

    column_formatters = {
        "user": lambda m, _: m.user.full_name if m.user else None,
    }


class RefreshTokenAdmin(BaseAdmin, model=RefreshToken):
    name = "Refresh Token"
    name_plural = "Refresh Tokens"
    icon = "fa-solid fa-key"

    column_list = [
        "id",
        "user",
        "ip_address",
        "expires_at",
        "is_revoked",
        "created_at",
    ]

    column_formatters = {
        "user": lambda m, _: m.user.full_name if m.user else None,
    }


class SystemConfigAdmin(BaseAdmin, model=SystemConfig):
    name = "System Config"
    name_plural = "System Configs"
    icon = "fa-solid fa-cog"

    can_edit = True
    can_create = True
    can_delete = True

    column_list = [
        "id",
        "key",
        "value",
        "description",
        "created_at",
        "updated_at",
    ]
