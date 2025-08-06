# Constants and Configuration Centralization

This document describes the centralization of magic numbers and configuration values in the Flights Chatbot Assistant API.

## Overview

Previously, magic numbers like JWT expiration times, password minimum length, and other configuration values were scattered throughout the codebase. This refactoring centralizes all these values in a single constants file and makes them configurable via environment variables.

## New Constants File

A new file `api/src/constants.py` has been created that contains:

### SecurityConstants

- `DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30` - Default JWT token expiration (was hardcoded as 30 minutes in multiple files)
- `MIN_PASSWORD_LENGTH = 8` - Minimum password length requirement
- `JWT_ALGORITHM = "HS256"` - JWT algorithm
- `COOKIE_MAX_AGE_SECONDS = 30 * 60` - Cookie max age in seconds
- `COOKIE_SAME_SITE = "lax"` - Cookie SameSite setting

### TimeConstants

- `THIRTY_MINUTES = 30`
- `ONE_HOUR = 60`
- `ONE_DAY = 24 * 60`
- `ONE_WEEK = 7 * 24 * 60`

### ApplicationConstants

- `DEFAULT_PORT = 8000`
- `DEFAULT_LOG_LEVEL = "INFO"`
- `DEFAULT_LOG_FILE = "logs/flights-chatbot.log"`
- `DEFAULT_DATABASE_URL = "sqlite:///./flights.db"`

### EnvironmentKeys

All environment variable keys are now centralized in one place.

## Environment Variable Configuration

The JWT token expiration time is now configurable via the `ACCESS_TOKEN_EXPIRE_MINUTES` environment variable:

```bash
# Set custom JWT expiration time (default is 30 minutes)
export ACCESS_TOKEN_EXPIRE_MINUTES=60  # 1 hour
export ACCESS_TOKEN_EXPIRE_MINUTES=15  # 15 minutes
```

## Helper Functions

The constants file provides helper functions:

- `get_env_int(key, default)` - Get integer values from environment variables
- `get_env_str(key, default)` - Get string values from environment variables
- `get_access_token_expire_minutes()` - Get the configured token expiration time
- `get_cookie_max_age_seconds()` - Get cookie max age based on token expiration

## Files Updated

The following files have been updated to use the centralized constants:

1. **`api/src/resources/crypto.py`**
   - Updated to use centralized constants and environment variables
   - JWT expiration now uses `ACCESS_TOKEN_EXPIRE_MINUTES` env var

2. **`api/src/services/user.py`**
   - Uses `SecurityConstants.MIN_PASSWORD_LENGTH` instead of hardcoded 8
   - Uses crypto manager's configured expiration time instead of hardcoded 30 minutes

3. **`api/src/routers/users.py`**
   - Uses `get_cookie_max_age_seconds()` for cookie configuration
   - Uses crypto manager's configured expiration time

4. **`api/src/resources/database.py`**
   - Uses centralized environment key constants

5. **`api/src/resources/logging.py`**
   - Uses centralized environment key constants

6. **`api/src/main.py`**
   - Uses centralized PORT configuration

7. **`api/src/services/health.py`**
   - Uses centralized Azure Speech environment keys

8. **`api/src/resources/chat.py`**
   - Uses centralized PORT configuration

## Benefits

1. **Single Source of Truth**: All magic numbers are now in one place
2. **Environment Configuration**: JWT expiration and other values can be configured via environment variables
3. **Maintainability**: Changes to default values only need to be made in one place
4. **Type Safety**: Helper functions provide better type safety for environment variables
5. **Documentation**: All constants are properly documented

## Usage Examples

### Setting Custom JWT Expiration

```bash
# For development (shorter sessions)
export ACCESS_TOKEN_EXPIRE_MINUTES=15

# For production (longer sessions)
export ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Docker Configuration

```yaml
environment:
  - ACCESS_TOKEN_EXPIRE_MINUTES=30
  - LOG_LEVEL=INFO
  - PORT=8000
```

## Migration Notes

- The default JWT expiration remains 30 minutes as before
- All existing functionality is preserved
- Environment variables are optional - defaults will be used if not set
- The change is backward compatible

This refactoring improves code maintainability and provides better configuration flexibility while maintaining the existing behavior by default.
