"""
Middleware package for the flights chatbot assistant API.
Contains authentication and other middleware components.
"""

from .auth import JWTAuthMiddleware, create_auth_middleware

__all__ = [
    "JWTAuthMiddleware",
    "create_auth_middleware"
]
