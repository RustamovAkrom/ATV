"""
Context-based Access Control (CAC) module.

Provides fine-grained authorization checks based on user context:
- Region-scoped access (user can only see/modify their region)
- Service-scoped access (user can only manage their service)
- User-created resources (only creator can delete)

This complements the base permission system for more nuanced control.
"""

from uuid import UUID

from core.exceptions.errors import PermissionDenied
from schemas.auth import CurrentUserSchema
from db.models.enums import UserRole

class AccessControl:
    """Handles context-based access control checks."""

    @staticmethod
    def _is_superadmin(user: CurrentUserSchema) -> bool:
        return user.role == UserRole.SUPERADMIN.value

    @staticmethod
    def check_region_access(user: CurrentUserSchema, resource_region_id: UUID | None):
        """
        Ensure user can only access resources in their assigned region.
        SuperAdmin and certain roles can bypass this.

        Args:
            user: Current user
            resource_region_id: Region ID of the resource

        Raises:
            PermissionDenied: If user doesn't have access to this region
        """
        # SuperAdmin has unrestricted access
        if AccessControl._is_superadmin(user):
            return

        if not user.assigned_region_id:
            raise PermissionDenied("User has no assigned region")

        if resource_region_id != user.assigned_region_id:
            raise PermissionDenied(
                f"Access denied. You can only access you region."
            )

    @staticmethod
    def check_service_access(user: CurrentUserSchema, resource_service_id: UUID | None):
        """
        Ensure user can only access resources in their assigned service.
        SuperAdmin and certain roles can bypass this.

        Args:
            user: Current user
            resource_service_id: Service ID of the resource

        Raises:
            PermissionDenied: If user doesn't have access to this service
        """
        # SuperAdmin has unrestricted access
        if AccessControl._is_superadmin(user):
            return

        if not user.assigned_service_id:
            raise PermissionDenied("User has no assigned service")

        if user.assigned_service_id != resource_service_id:
            raise PermissionDenied(
                detail=f"Access denied. You can only access your service."
            )

    @staticmethod
    def check_creator_access(user: CurrentUserSchema, resource_creator_id: UUID):
        """
        Ensure user is the creator of a resource (used for deletion/modification).

        Args:
            user: Current user
            resource_creator_id: ID of the user who created the resource

        Raises:
            PermissionDenied: If user is not the creator
        """
        # SuperAdmin can modify any resource
        if AccessControl._is_superadmin(user):
            return

        if user.id != resource_creator_id:
            raise PermissionDenied(
                detail="Only the creator can modify this resource."
            )

    @staticmethod
    def check_not_creator(user: CurrentUserSchema, resource_creator_id: UUID):
        """
        Ensure user is NOT the creator (used in approval workflows).
        Creator cannot approve/reject their own request.

        Args:
            user: Current user
            resource_creator_id: ID of the user who created the resource

        Raises:
            PermissionDenied: If user is the creator
        """
        if user.id == resource_creator_id:
            raise PermissionDenied(
                detail="You cannot approve/reject your own requests."
            )

    @staticmethod
    def check_multi_level_approval(
        user: CurrentUserSchema,
        created_by_id: UUID,
        approved_by_id: UUID | None,
        required_role: str | None = None,
    ):
        """
        Check if user can approve at this stage in multi-level approval workflow.

        Rules:
        - Creator cannot approve their own request
        - Different approvers at different levels
        - Can't approve if already approved by someone else

        Args:
            user: Current user
            created_by_id: Who created the request
            approved_by_id: Who already approved (if any)
            required_role: Minimum role required (e.g., "admin")

        Raises:
            PermissionDenied: If checks fail
        """
        # Check creator
        AccessControl.check_not_creator(user, created_by_id)

        # Check if already approved at this level
        if approved_by_id:
            raise PermissionDenied("This request is already decided")

        # Check required role
        if required_role and user.role != required_role:
            raise PermissionDenied(
                detail=f"This approval requires '{required_role}' role."
            )


def require_region_access(region_id: UUID | None):
    """
    FastAPI dependency for region-scoped access.

    Usage:
        @router.get("/")
        async def get_resources(
            user: CurrentUserSchema = Depends(get_current_user),
            _: None = Depends(require_region_access(my_region_id))
        ):
            ...
    """
    def checker(user: CurrentUserSchema):
        AccessControl.check_region_access(user, region_id)
        return None

    return checker


def require_service_access(service_id: UUID | None):
    """FastAPI dependency for service-scoped access."""
    def checker(user: CurrentUserSchema):
        AccessControl.check_service_access(user, service_id)
        return None

    return checker
