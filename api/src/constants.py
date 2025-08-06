"""
Application constants and configuration values.
Centralizes magic numbers and configuration parameters.
"""

import os
from typing import Dict, Any

class SecurityConstants:
    """Security-related constants."""
    
    # JWT Token Configuration
    DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    MIN_PASSWORD_LENGTH = 8
    JWT_ALGORITHM = "HS256"
    
    # Cookie Configuration
    COOKIE_MAX_AGE_SECONDS = 30 * 60  # 30 minutes in seconds
    COOKIE_SAME_SITE = "lax"
    
    # Default secret key warning message
    DEFAULT_SECRET_KEY_WARNING = "please_guys_do_not_forget_to_set_a_secret_key"
    
    # Middleware Configuration - Paths that don't require authentication
    EXCLUDED_PATHS = [
        "/",
        "/docs",
        "/openapi.json", 
        "/redoc",
        "/health",
        "/users/register",
        "/users/login",
        "/flights/search",  # Public flight search
        "/flights/list"     # Public flight listing
    ]

class TimeConstants:
    """Time-related constants."""
    
    # Common time intervals in minutes
    THIRTY_MINUTES = 30
    ONE_HOUR = 60
    ONE_DAY = 24 * 60
    ONE_WEEK = 7 * 24 * 60

class ApplicationConstants:
    """General application constants."""
    
    # Default values
    DEFAULT_PORT = 8000
    DEFAULT_LOG_LEVEL = "INFO"
    DEFAULT_LOG_FILE = "logs/flights-chatbot.log"
    DEFAULT_DATABASE_URL = "sqlite:///./flights.db"

class EnvironmentKeys:
    """Environment variable keys."""
    
    SECRET_KEY = "SECRET_KEY"
    ACCESS_TOKEN_EXPIRE_MINUTES = "ACCESS_TOKEN_EXPIRE_MINUTES"
    PORT = "PORT"
    LOG_LEVEL = "LOG_LEVEL"
    LOG_FILE = "LOG_FILE"
    ERROR_LOG_FILE = "ERROR_LOG_FILE"
    DATABASE_URL = "DATABASE_URL"
    AZURE_SPEECH_KEY = "AZURE_SPEECH_KEY"
    AZURE_SPEECH_REGION = "AZURE_SPEECH_REGION"
    AZURE_SPEECH_ENDPOINT = "AZURE_SPEECH_ENDPOINT"

def get_env_int(key: str, default: int) -> int:
    """Get an integer value from environment variables with a default fallback."""
    try:
        value = os.getenv(key)
        if value is not None:
            return int(value)
        return default
    except (ValueError, TypeError):
        return default

def get_env_str(key: str, default: str) -> str:
    """Get a string value from environment variables with a default fallback."""
    return os.getenv(key, default)

def get_access_token_expire_minutes() -> int:
    """Get the access token expiration time in minutes from environment or default."""
    return get_env_int(
        EnvironmentKeys.ACCESS_TOKEN_EXPIRE_MINUTES, 
        SecurityConstants.DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

def get_cookie_max_age_seconds() -> int:
    """Get the cookie max age in seconds based on token expiration time."""
    return get_access_token_expire_minutes() * 60  # Convert minutes to seconds

def get_excluded_paths() -> list:
    """Get the list of paths excluded from authentication."""
    return SecurityConstants.EXCLUDED_PATHS
