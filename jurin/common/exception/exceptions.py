from rest_framework import status

from jurin.common.base.exception import BaseAPIException


class UnknownServerException(BaseAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "An unknown server error occurred."
    default_code = "unknown_server_error"


class InvalidParameterFormatException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "The parameter format is incorrect."
    default_code = "invalid_parameter_format"


class AuthenticationFailedException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Incorrect authentication credentials."
    default_code = "authentication_failed"


class InvalidTokenException(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token is invalid or expired"
    default_code = "token_not_valid"


class ValidationException(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation failed."
    default_code = "validation_failed"


class NotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Not found."
    default_code = "not_found"


class PermissionDeniedException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permission to perform this action."
    default_code = "permission_denied"


class TaskFailedException(BaseAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Task failed."
    default_code = "task_failed"
