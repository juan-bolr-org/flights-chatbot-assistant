from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .chat import chat_manager
from .crypto import crypto_manager, CryptoManager
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.sqlite import SqliteSaver
from repository.user import User

# Security
security = HTTPBearer()

def get_chat_model() -> BaseChatModel:
    """Dependency function to get the chat model."""
    return chat_manager.get_response_model()


def get_chat_memory() -> SqliteSaver:
    """Dependency function to get the chat checkpointer."""
    return chat_manager.get_memory()


def get_faq_tool():
    """Dependency function to get the FAQ tool."""
    return chat_manager.get_faq_tool()


def get_system_context() -> str:
    """Dependency function to get the system context."""
    return chat_manager.get_system_context()


def get_crypto_manager() -> CryptoManager:
    """Dependency function to get the crypto manager."""
    return crypto_manager


def get_current_user(request: Request) -> User:
    """
    Dependency function to get the current authenticated user from middleware.
    The middleware validates the JWT token and stores the user in request.state.
    """
    try:
        # Get user from request state (set by auth middleware)
        user = getattr(request.state, 'current_user', None)
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        return user
    except AttributeError:
        raise HTTPException(status_code=401, detail="Authentication required")

