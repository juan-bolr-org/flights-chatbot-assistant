from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Generator
from .database import db_manager
from .chat import chat_manager
from .crypto import crypto_manager, CryptoManager
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from models import User


# Security
security = HTTPBearer()


def get_database_session() -> Generator[Session, None, None]:
    """Dependency function to get a database session."""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def get_chat_model() -> BaseChatModel:
    """Dependency function to get the chat model."""
    return chat_manager.get_response_model()


def get_chat_memory() -> MemorySaver:
    """Dependency function to get the chat memory."""
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


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_database_session)
) -> User:
    """Dependency function to get the current authenticated user."""
    try:
        token = credentials.credentials
        crypto = crypto_manager
        email = crypto.get_token_subject(token)
        
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


def get_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user: User = Depends(get_current_user)
):
    """Dependency function to get a configured agent for the current user."""
    token = credentials.credentials
    return chat_manager.create_agent(user_token=token, user_id=user.id)
    

