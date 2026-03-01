from __future__ import annotations


class AppError(Exception):
    def __init__(self, error: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.error = error
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    def __init__(self, message: str, error: str = "VALIDATION_ERROR") -> None:
        super().__init__(error=error, message=message, status_code=400)


class NotFoundError(AppError):
    def __init__(self, message: str, error: str = "NOT_FOUND") -> None:
        super().__init__(error=error, message=message, status_code=404)


class ConflictError(AppError):
    def __init__(self, message: str, error: str = "CONFLICT") -> None:
        super().__init__(error=error, message=message, status_code=409)
