"""
Custom exception hierarchy for the flights chatbot API.
Provides type-safe, structured error handling similar to Rust's Result types (I like strong typing).
"""

from typing import Optional
from enum import Enum


class ErrorCode(Enum):
    """Error codes for different types of business logic errors."""
    # User errors
    USER_NOT_FOUND = "USER_NOT_FOUND"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    
    # Flight errors
    FLIGHT_NOT_FOUND = "FLIGHT_NOT_FOUND"
    FLIGHT_NOT_AVAILABLE = "FLIGHT_NOT_AVAILABLE"
    INVALID_DATE_FORMAT = "INVALID_DATE_FORMAT"
    INVALID_FLIGHT_TIMES = "INVALID_FLIGHT_TIMES"
    INVALID_FLIGHT_PRICE = "INVALID_FLIGHT_PRICE"
    
    # Booking errors
    BOOKING_NOT_FOUND = "BOOKING_NOT_FOUND"
    BOOKING_ALREADY_EXISTS = "BOOKING_ALREADY_EXISTS"
    BOOKING_CANNOT_BE_CANCELLED = "BOOKING_CANNOT_BE_CANCELLED"
    PAST_FLIGHT_CANNOT_BE_CANCELLED = "PAST_FLIGHT_CANNOT_BE_CANCELLED"
    ACCESS_DENIED = "ACCESS_DENIED"
    
    # Chat errors
    CHAT_MESSAGE_SAVE_FAILED = "CHAT_MESSAGE_SAVE_FAILED"
    AGENT_INVOCATION_FAILED = "AGENT_INVOCATION_FAILED"
    
    # Speech errors
    SPEECH_SERVICE_NOT_CONFIGURED = "SPEECH_SERVICE_NOT_CONFIGURED"
    INVALID_AUDIO_FILE = "INVALID_AUDIO_FILE"
    SPEECH_RECOGNITION_FAILED = "SPEECH_RECOGNITION_FAILED"
    NO_SPEECH_DETECTED = "NO_SPEECH_DETECTED"


class ApiException(Exception):
    """Base exception for all API business logic errors."""
    
    def __init__(self, error_code: ErrorCode, message: str, details: Optional[dict] = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            "error_code": self.error_code.value,
            "message": self.message,
            "details": self.details
        }


# User-related exceptions
class UserNotFoundError(ApiException):
    def __init__(self, email: str):
        super().__init__(
            ErrorCode.USER_NOT_FOUND,
            f"User with email {email} not found",
            {"email": email}
        )


class EmailAlreadyExistsError(ApiException):
    def __init__(self, email: str):
        super().__init__(
            ErrorCode.EMAIL_ALREADY_EXISTS,
            "Email already registered",
            {"email": email}
        )


class InvalidCredentialsError(ApiException):
    def __init__(self):
        super().__init__(
            ErrorCode.INVALID_CREDENTIALS,
            "Incorrect email or password"
        )


# Flight-related exceptions
class FlightNotFoundError(ApiException):
    def __init__(self, flight_id: int):
        super().__init__(
            ErrorCode.FLIGHT_NOT_FOUND,
            f"Flight {flight_id} not found",
            {"flight_id": flight_id}
        )


class FlightNotAvailableError(ApiException):
    def __init__(self, flight_id: int):
        super().__init__(
            ErrorCode.FLIGHT_NOT_AVAILABLE,
            f"Flight {flight_id} is not available for booking",
            {"flight_id": flight_id}
        )


class InvalidDateFormatError(ApiException):
    def __init__(self, date_string: str):
        super().__init__(
            ErrorCode.INVALID_DATE_FORMAT,
            f"Invalid date format: {date_string}. Use YYYY-MM-DD",
            {"provided_date": date_string}
        )


class InvalidFlightTimesError(ApiException):
    def __init__(self, departure_time: str, arrival_time: str):
        super().__init__(
            ErrorCode.INVALID_FLIGHT_TIMES,
            f"Departure time ({departure_time}) must be before arrival time ({arrival_time})",
            {"departure_time": departure_time, "arrival_time": arrival_time}
        )


class InvalidFlightPriceError(ApiException):
    def __init__(self, price: float):
        super().__init__(
            ErrorCode.INVALID_FLIGHT_PRICE,
            f"Flight price ({price}) must be greater than 0",
            {"provided_price": price}
        )


# Booking-related exceptions
class BookingNotFoundError(ApiException):
    def __init__(self, booking_id: int):
        super().__init__(
            ErrorCode.BOOKING_NOT_FOUND,
            f"Booking {booking_id} not found",
            {"booking_id": booking_id}
        )


class BookingAlreadyExistsError(ApiException):
    def __init__(self, user_id: int, flight_id: int):
        super().__init__(
            ErrorCode.BOOKING_ALREADY_EXISTS,
            "You already have a booking for this flight",
            {"user_id": user_id, "flight_id": flight_id}
        )


class BookingCannotBeCancelledError(ApiException):
    def __init__(self, booking_id: int, current_status: str):
        super().__init__(
            ErrorCode.BOOKING_CANNOT_BE_CANCELLED,
            f"Only booked flights can be cancelled. Current status: {current_status}",
            {"booking_id": booking_id, "current_status": current_status}
        )


class PastFlightCannotBeCancelledError(ApiException):
    def __init__(self, booking_id: int, flight_id: int):
        super().__init__(
            ErrorCode.PAST_FLIGHT_CANNOT_BE_CANCELLED,
            "Cannot cancel past flights",
            {"booking_id": booking_id, "flight_id": flight_id}
        )


class AccessDeniedError(ApiException):
    def __init__(self, resource_type: str, resource_id: int, user_id: int):
        super().__init__(
            ErrorCode.ACCESS_DENIED,
            f"Access denied to {resource_type} {resource_id}",
            {"resource_type": resource_type, "resource_id": resource_id, "user_id": user_id}
        )


# Chat-related exceptions
class ChatMessageSaveFailedError(ApiException):
    def __init__(self, user_id: int, error_details: str):
        super().__init__(
            ErrorCode.CHAT_MESSAGE_SAVE_FAILED,
            "Failed to save chat message to database",
            {"user_id": user_id, "error_details": error_details}
        )


class AgentInvocationFailedError(ApiException):
    def __init__(self, user_id: int, error_details: str):
        super().__init__(
            ErrorCode.AGENT_INVOCATION_FAILED,
            "Failed to process chat request",
            {"user_id": user_id, "error_details": error_details}
        )


# Speech-related exceptions
class SpeechServiceNotConfiguredError(ApiException):
    def __init__(self):
        super().__init__(
            ErrorCode.SPEECH_SERVICE_NOT_CONFIGURED,
            "Azure Speech Service is not properly configured"
        )


class InvalidAudioFileError(ApiException):
    def __init__(self, content_type: str = None):
        details = {"content_type": content_type} if content_type else {}
        super().__init__(
            ErrorCode.INVALID_AUDIO_FILE,
            "File must be a valid audio file",
            details
        )


class SpeechRecognitionFailedError(ApiException):
    def __init__(self, reason: str = None):
        details = {"reason": reason} if reason else {}
        super().__init__(
            ErrorCode.SPEECH_RECOGNITION_FAILED,
            "Speech recognition service failed to process the audio",
            details
        )


class NoSpeechDetectedError(ApiException):
    def __init__(self):
        super().__init__(
            ErrorCode.NO_SPEECH_DETECTED,
            "No speech was detected in the audio file"
        )
