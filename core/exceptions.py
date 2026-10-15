from typing import Optional


class BaseAPIException(Exception):
    status_code: int = 500
    detail: str = "Internal Server Error"

    def __init__(self, detail: Optional[str] = None, status_code: Optional[int] = None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code


class NotFoundException(BaseAPIException):
    status_code = 404
    detail = "Resource not found"

class ValidationException(BaseAPIException):
    status_code = 422
    detail = "Validation error"

class UnauthorizedException(BaseAPIException):
    status_code = 401
    detail = "Not authenticated"

class ForbiddenException(BaseAPIException):
    status_code = 403
    detail = "Permission denied"