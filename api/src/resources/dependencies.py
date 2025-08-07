from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .chat import chat_manager
from .crypto import crypto_manager, CryptoManager
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.state import CompiledStateGraph
from repository.user import UserRepository, create_user_repository, User
from typing import Optional

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


def get_current_user_legacy(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    user_repository: UserRepository = Depends(create_user_repository)
) -> User:
    """
    Legacy dependency function for backwards compatibility.
    Use get_current_user instead - this validates tokens independently of middleware.
    """
    try:
        token = credentials.credentials
        crypto = crypto_manager
        email = crypto.get_token_subject(token)
        
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = user_repository.find_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


def get_agent(
    request: Request,
    user: User = Depends(get_current_user),
    session_id: Optional[str] = None
) -> CompiledStateGraph:
    """
    Dependency function to get a configured agent for the current user.
    Uses JWT token from middleware state and supports optional session ID.
    """
    # Get token from request state (set by auth middleware)
    token = getattr(request.state, 'jwt_token', None)
    if not token:
        raise HTTPException(status_code=401, detail="No authentication token available")
    
    return chat_manager.create_agent(user_token=token, user_id=user.id, session_id=session_id)
    

