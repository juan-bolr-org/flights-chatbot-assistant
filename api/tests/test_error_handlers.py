"""
Tests for error handlers utility functions.
"""
import pytest
from unittest.mock import Mock
from fastapi import HTTPException

# Add src to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.error_handlers import api_exception_to_http_exception, handle_api_exceptions
from exceptions import (
    ApiException, 
    ErrorCode, 
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    AccessDeniedError,
    UserNotFoundError,
    FlightNotFoundError,
    BookingNotFoundError,
    AgentInvocationFailedError,
    InvalidAudioFileError
)


class TestErrorHandlers:
    """Test suite for error handling utilities."""
    
    def test_api_exception_to_http_exception_email_exists(self):
        """Test conversion of EmailAlreadyExistsError to HTTPException."""
        api_exc = EmailAlreadyExistsError("test@example.com")
        http_exc = api_exception_to_http_exception(api_exc)
        
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 400
        assert http_exc.detail["error_code"] == "EMAIL_ALREADY_EXISTS"
        assert http_exc.detail["message"] == "Email already registered"
    
    def test_api_exception_to_http_exception_invalid_credentials(self):
        """Test conversion of InvalidCredentialsError to HTTPException."""
        api_exc = InvalidCredentialsError()
        http_exc = api_exception_to_http_exception(api_exc)
        
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 401
        assert http_exc.detail["error_code"] == "INVALID_CREDENTIALS"
    
    def test_api_exception_to_http_exception_access_denied(self):
        """Test conversion of AccessDeniedError to HTTPException."""
        api_exc = AccessDeniedError("booking", 123, 456)
        http_exc = api_exception_to_http_exception(api_exc)
        
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 403
        assert http_exc.detail["error_code"] == "ACCESS_DENIED"
    
    def test_api_exception_to_http_exception_not_found(self):
        """Test conversion of NotFound errors to HTTPException."""
        # Test UserNotFoundError
        api_exc = UserNotFoundError(123)
        http_exc = api_exception_to_http_exception(api_exc)
        assert http_exc.status_code == 404
        assert http_exc.detail["error_code"] == "USER_NOT_FOUND"
        
        # Test FlightNotFoundError
        api_exc = FlightNotFoundError(456)
        http_exc = api_exception_to_http_exception(api_exc)
        assert http_exc.status_code == 404
        assert http_exc.detail["error_code"] == "FLIGHT_NOT_FOUND"
        
        # Test BookingNotFoundError
        api_exc = BookingNotFoundError(789)
        http_exc = api_exception_to_http_exception(api_exc)
        assert http_exc.status_code == 404
        assert http_exc.detail["error_code"] == "BOOKING_NOT_FOUND"
    
    def test_api_exception_to_http_exception_internal_server_error(self):
        """Test conversion of internal server errors to HTTPException."""
        api_exc = AgentInvocationFailedError(123, "Chat agent failed")
        http_exc = api_exception_to_http_exception(api_exc)
        
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 500
        assert http_exc.detail["error_code"] == "AGENT_INVOCATION_FAILED"
    
    def test_api_exception_to_http_exception_unprocessable_entity(self):
        """Test conversion of validation errors to HTTPException."""
        api_exc = InvalidAudioFileError("Unsupported format")
        http_exc = api_exception_to_http_exception(api_exc)
        
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 422
        assert http_exc.detail["error_code"] == "INVALID_AUDIO_FILE"
    
    def test_api_exception_to_http_exception_unknown_error_code(self):
        """Test conversion of unknown error code defaults to 500."""
        # Create a custom ApiException with unknown error code
        class CustomApiException(ApiException):
            def __init__(self):
                # Create a mock ErrorCode that's not in the mapping
                mock_error_code = Mock()
                mock_error_code.value = "UNKNOWN_ERROR"
                super().__init__(mock_error_code, "Unknown error occurred", {})
        
        api_exc = CustomApiException()
        http_exc = api_exception_to_http_exception(api_exc)
        
        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == 500
    
    def test_handle_api_exceptions_decorator_success(self):
        """Test handle_api_exceptions decorator when function succeeds."""
        @handle_api_exceptions
        def test_function():
            return "success"
        
        result = test_function()
        assert result == "success"
    
    def test_handle_api_exceptions_decorator_with_api_exception(self):
        """Test handle_api_exceptions decorator converts ApiException to HTTPException."""
        @handle_api_exceptions
        def test_function():
            raise EmailAlreadyExistsError("test@example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            test_function()
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail["error_code"] == "EMAIL_ALREADY_EXISTS"
    
    def test_handle_api_exceptions_decorator_with_non_api_exception(self):
        """Test handle_api_exceptions decorator passes through non-ApiExceptions."""
        @handle_api_exceptions
        def test_function():
            raise ValueError("Regular exception")
        
        with pytest.raises(ValueError) as exc_info:
            test_function()
        
        assert str(exc_info.value) == "Regular exception"
    
    def test_handle_api_exceptions_decorator_with_args_kwargs(self):
        """Test handle_api_exceptions decorator preserves function arguments."""
        @handle_api_exceptions
        def test_function(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"
        
        result = test_function("a", "b", kwarg1="c")
        assert result == "a-b-c"
