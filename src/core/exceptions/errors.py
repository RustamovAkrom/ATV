from .base import APIException


class PermissionDenied(APIException):
    status_code = 403
    code = "permission_denied"
    detail = "You do not have permission to perform this action."


class NotFound(APIException):
    status_code = 404
    code = "not_found"
    detail = "Requested resource was not found."


class Conflict(APIException):
    status_code = 409
    code = "conflict"
    detail = "Resource conflict occurred."


class ValidationError(APIException):
    status_code = 422
    code = "validation_error"
    detail = "Invalid request data."


class AuthenticationError(APIException):
    status_code = 401
    code = "authentication_failed"
    detail = "Authentication failed."


class RateLimitExceeded(APIException):
    status_code = 429
    code = "rate_limit_exceeded"
    detail = "Too many requests."
