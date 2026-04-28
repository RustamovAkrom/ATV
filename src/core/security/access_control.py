"""
Context-based Access Control (CAC) module.

Provides fine-grained authorization checks based on user context:
- Region-scoped access (user can only see/modify their region)
- Service-scoped access (user can only manage their service)
- User-created resources (only creator can delete)

This complements the base permission system for more nuanced control.
"""

from uuid import UUID

from fastapi import Depends
from core.exceptions.errors import PermissionDenied
from schemas.auth import CurrentUserSchema
from db.models.enums import ApprovalStatus, UserRole
from core.security.auth.dependencies import get_current_user


class AccessControl:
    """Handles context-based access control checks."""

    # INTERNAL METHODS
    @staticmethod
    def _is_superadmin(user: CurrentUserSchema) -> bool:
        return user.role == UserRole.SUPERADMIN.value

    @staticmethod
    def _is_global_role(user: CurrentUserSchema) -> bool:
        """
        Roles that are NOT restricted by region/service.
        """

        return user.role in {
            UserRole.SUPERADMIN.value,
            UserRole.ADMIN.value,
            UserRole.ANALYTIC.value,
            UserRole.AUDITOR.value,
        }

    # REGION ACCESS
    @staticmethod
    def check_region_access(user: CurrentUserSchema, resource_region_id: UUID | None):
        if AccessControl._is_global_role(user):
            return

        if not user.assigned_region_id:
            raise PermissionDenied("User has no assigned region")

        if resource_region_id is None:
            raise PermissionDenied("Resource has no region assigned")

        if resource_region_id != user.assigned_region_id:
            raise PermissionDenied("Access denied: region mismatch")

    # SERVICE ACCESS
    @staticmethod
    def check_service_access(user: CurrentUserSchema, resource_service_id: UUID | None):
        if AccessControl._is_global_role(user):
            return

        if not user.assigned_service_id:
            raise PermissionDenied("User has no assigned service")

        if resource_service_id is None:
            raise PermissionDenied("Resource has no service assigned")

        if user.assigned_service_id != resource_service_id:
            raise PermissionDenied("Access denied: service scope violation")

    # CREATOR ACCESS
    @staticmethod
    def check_creator_access(user: CurrentUserSchema, resource_creator_id: UUID):
        if AccessControl._is_superadmin(user):
            return

        if user.id != resource_creator_id:
            raise PermissionDenied("Only the creator can modify this resource.")

    @staticmethod
    def check_not_creator(
        user: CurrentUserSchema,
        resource_creator_id: UUID,
    ):
        if user.id == resource_creator_id:
            raise PermissionDenied("You cannot approve/reject your own requests.")

    # APPROVAL SECURITY
    @staticmethod
    def check_multi_level_approval(
        user: CurrentUserSchema,
        created_by_id: UUID,
        approved_by_id: UUID | None,
        status: str,
        required_role: str | None,
    ):
        # creator restriction
        AccessControl.check_not_creator(user, created_by_id)

        # status check
        if status != ApprovalStatus.PENDING:
            raise PermissionDenied("Only pending requests can be approved/rejected")

        # already decided
        if approved_by_id:
            raise PermissionDenied("Already decided")

        # role restriction
        if required_role and user.role != required_role:
            raise PermissionDenied(f"This approval requires '{required_role}' role.")


# FASTAPI DEPENDENCIES
def require_region_access(region_id: UUID | None):
    def checker(user: CurrentUserSchema = Depends(get_current_user)):
        AccessControl.check_region_access(user, region_id)
        return None

    return checker


def require_service_access(service_id: UUID | None):
    def checker(user: CurrentUserSchema = Depends(get_current_user)):
        AccessControl.check_service_access(user, service_id)
        return None

    return checker
