"""
Utility functions for converting structured exceptions to HTTP responses.
Provides centralized, type-safe error handling for FastAPI routers.
"""

from fastapi import HTTPException
from exceptions import ApiException, ErrorCode


def api_exception_to_http_exception(exc: ApiException) -> HTTPException:
    """
    Convert a structured ApiException to FastAPI HTTPException.
    Provides centralized mapping of business errors to HTTP status codes.
    """
    # Mapping of error codes to HTTP status codes
    status_code_mapping = {
        # 400 Bad Request - Client errors
        ErrorCode.EMAIL_ALREADY_EXISTS: 400,
        ErrorCode.BOOKING_ALREADY_EXISTS: 400,
        ErrorCode.BOOKING_CANNOT_BE_CANCELLED: 400,
        ErrorCode.PAST_FLIGHT_CANNOT_BE_CANCELLED: 400,
        ErrorCode.INVALID_DATE_FORMAT: 400,
        ErrorCode.INVALID_FLIGHT_TIMES: 400,
        ErrorCode.INVALID_FLIGHT_PRICE: 400,
        ErrorCode.CHAT_MESSAGE_SAVE_FAILED: 400,
        
        # 401 Unauthorized - Authentication errors
        ErrorCode.INVALID_CREDENTIALS: 401,
        
        # 403 Forbidden - Authorization errors
        ErrorCode.ACCESS_DENIED: 403,
        
        # 404 Not Found - Resource not found
        ErrorCode.USER_NOT_FOUND: 404,
        ErrorCode.FLIGHT_NOT_FOUND: 404,
        ErrorCode.FLIGHT_NOT_AVAILABLE: 404,
        ErrorCode.BOOKING_NOT_FOUND: 404,
        
        # 500 Internal Server Error - System errors
        ErrorCode.AGENT_INVOCATION_FAILED: 500,
    }
    
    status_code = status_code_mapping.get(exc.error_code, 500)
    
    return HTTPException(
        status_code=status_code,
        detail=exc.to_dict()
    )


def handle_api_exceptions(func):
    """
    Decorator to automatically convert ApiExceptions to HTTPExceptions.
    Usage: @handle_api_exceptions
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ApiException as e:
            raise api_exception_to_http_exception(e)
    return wrapper
