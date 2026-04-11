# src/core/exceptions/errors.py

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
    detail = "Invalid login or password."


class TokenExpired(APIException):
    status_code = 401
    code = "token_expired"
    detail = "Token has expired."


class InvalidToken(APIException):
    status_code = 401
    code = "invalid_token"
    detail = "Invalid authentication token."


class RateLimitExceeded(APIException):
    status_code = 429
    code = "rate_limit_exceeded"
    detail = "Too many requests."


class InternalError(APIException):
    status_code = 500
    code = "internal_error"
    detail = "Internal server error."
