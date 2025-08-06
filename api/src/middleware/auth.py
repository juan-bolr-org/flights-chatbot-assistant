"""
JWT Authentication Middleware for FastAPI application.
Handles authentication for all protected endpoints using JWT Bearer tokens.
"""

from fastapi import Request, Response, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Optional
import re
from resources.crypto import crypto_manager
from resources.database import get_database_session
from repository.user import UserSqliteRepository
from resources.logging import get_logger

logger = get_logger("auth_middleware")


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware that validates tokens for protected endpoints.
    Supports both Authorization header and cookie-based authentication.
    """
    
    def __init__(self, app, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        # Default excluded paths that don't need authentication
        self.excluded_paths = excluded_paths or [
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
        # Compile regex patterns for excluded paths using a helper method
        self.excluded_patterns = [self._compile_path_pattern(pattern) for pattern in self.excluded_paths]
    
    def _compile_path_pattern(self, pattern: str) -> re.Pattern:
        """
        Compiles a path pattern (with optional wildcards) into a regex pattern.
        Wildcards (*) are converted to match any character sequence.
        """
        # Escape all regex special characters except for '*'
        escaped = re.escape(pattern)
        # Replace escaped '*' (which is '\*') with '.*' to match any characters
        regex_pattern = f"^{escaped.replace(r'\\*', '.*')}$"
        return re.compile(regex_pattern)
    async def dispatch(self, request: Request, call_next):
        """
        Main middleware dispatch method.
        Validates JWT tokens for protected endpoints.
        """
        try:
            # Check if the path is excluded from authentication
            if self._is_path_excluded(request.url.path):
                logger.debug(f"Path {request.url.path} is excluded from authentication")
                return await call_next(request)
            
            # Extract JWT token from request
            token = self._extract_token(request)
            if not token:
                logger.warning(f"No token provided for protected endpoint: {request.url.path}")
                return self._create_unauthorized_response("No authentication token provided")
            
            # Validate token and get user
            user = await self._validate_token_and_get_user(token)
            if not user:
                logger.warning(f"Invalid token for endpoint: {request.url.path}")
                return self._create_unauthorized_response("Invalid or expired token")
            
            # Store user information in request state for use in endpoints
            request.state.current_user = user
            request.state.jwt_token = token
            
            logger.debug(f"Authenticated user {user.email} for endpoint: {request.url.path}")
            
            # Continue to the next middleware or endpoint
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            logger.error(f"HTTP exception in auth middleware: {e.detail}")
            return self._create_error_response(e.status_code, e.detail)
        except Exception as e:
            logger.error(f"Unexpected error in auth middleware: {e}", exc_info=True)
            return self._create_error_response(500, "Internal server error")
    
    def _is_path_excluded(self, path: str) -> bool:
        """Check if the given path is excluded from authentication."""
        for pattern in self.excluded_patterns:
            if pattern.match(path):
                return True
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """
        Extract JWT token from Authorization header or cookies.
        Supports both 'Bearer <token>' format and cookie-based tokens.
        """
        # Try Authorization header first
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer" and token:
                return token
        
        # Fallback to cookie-based token
        token = request.cookies.get("access_token")
        if token:
            return token
        
        return None
    
    async def _validate_token_and_get_user(self, token: str):
        """
        Validate JWT token and retrieve user from database.
        Returns user object if valid, None otherwise.
        """
        try:
            # Validate token using crypto manager
            email = crypto_manager.get_token_subject(token)
            if not email:
                logger.debug("Token validation failed: no email in token")
                return None
            
            # Get user from database
            db_session = next(get_database_session())
            try:
                user_repository = UserSqliteRepository(db_session)
                user = user_repository.find_by_email(email)
                
                if not user:
                    logger.debug(f"User not found in database: {email}")
                    return None
                
                logger.debug(f"Successfully validated user: {email}")
                return user
                
            finally:
                db_session.close()
                
        except Exception as e:
            logger.error(f"Error validating token: {e}", exc_info=True)
            return None
    
    def _create_unauthorized_response(self, message: str) -> Response:
        """Create a 401 Unauthorized response."""
        return Response(
            content=f'{{"detail": "{message}"}}',
            status_code=401,
            media_type="application/json"
        )
    
    def _create_error_response(self, status_code: int, message: str) -> Response:
        """Create an error response with the given status code and message."""
        return Response(
            content=f'{{"detail": "{message}"}}',
            status_code=status_code,
            media_type="application/json"
        )


def create_auth_middleware(excluded_paths: Optional[List[str]] = None) -> JWTAuthMiddleware:
    """
    Factory function to create JWT authentication middleware with custom excluded paths.
    
    Args:
        excluded_paths: List of path patterns to exclude from authentication.
                       Supports wildcards (e.g., "/public/*")
    
    Returns:
        Configured JWTAuthMiddleware instance
    """
    return JWTAuthMiddleware(None, excluded_paths)
