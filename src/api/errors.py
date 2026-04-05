"""Unified error response handling for Baby Diary API"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Any, Dict, Optional


class APIError(Exception):
    """Custom API error exception"""

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code


def create_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create standardized error response format"""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """Handler for custom APIError exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for request validation errors"""
    errors = exc.errors()
    error_details = []

    for error in errors:
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Invalid value")
        error_details.append({
            "field": loc,
            "message": msg,
        })

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=create_error_response(
            code="validation_error",
            message="Request validation failed",
            details={"errors": error_details},
        ),
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for unexpected exceptions"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            code="internal_error",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__},
        ),
    )


# Error code constants
ERROR_CODES = {
    # Authentication errors
    "invalid_token": "Invalid or expired authentication token",
    "missing_token": "Missing authentication token",
    "unauthorized": "Unauthorized access",
    "wechat_login_failed": "WeChat login failed",

    # Record errors
    "invalid_record_type": "Invalid record type",
    "record_not_found": "Record not found",
    "duplicate_record": "Duplicate record detected",

    # Config errors
    "invalid_date_format": "Invalid date format",

    # Validation errors
    "validation_error": "Request validation failed",

    # System errors
    "internal_error": "Internal server error",
    "database_error": "Database operation failed",
}