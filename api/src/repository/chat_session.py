from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import Depends
from resources.database import get_database_session
from models import ChatSession, ChatbotMessage
import datetime


class ChatSessionRepository(ABC):
    """Abstract base class for ChatSession repository operations."""
    
    @abstractmethod
    def create(self, user_id: int, session_id: str, alias: str) -> ChatSession:
        """Create a new chat session."""
        pass
    
    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Find a chat session by ID."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int) -> List[ChatSession]:
        """Find all chat sessions for a user."""
        pass
    
    @abstractmethod
    def find_by_user_and_session(self, user_id: int, session_id: str) -> Optional[ChatSession]:
        """Find a specific session for a user."""
        pass
    
    @abstractmethod
    def update_alias(self, user_id: int, session_id: str, alias: str) -> Optional[ChatSession]:
        """Update session alias."""
        pass
    
    @abstractmethod
    def delete_by_id(self, user_id: int, session_id: str) -> bool:
        """Delete a session by ID."""
        pass
    
    @abstractmethod
    def get_sessions_with_message_count(self, user_id: int) -> List[tuple]:
        """Get sessions with message counts for a user."""
        pass


class ChatSessionSqliteRepository(ChatSessionRepository):
    """SQLite implementation of ChatSessionRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, session_id: str, alias: str) -> ChatSession:
        """Create a new chat session."""
        # Prefix session_id with user_id for uniqueness
        prefixed_session_id = f"{user_id}_{session_id}"
        session = ChatSession(
            id=prefixed_session_id,
            user_id=user_id,
            alias=alias,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc)
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def find_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Find a chat session by ID."""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    def find_by_user_id(self, user_id: int) -> List[ChatSession]:
        """Find all chat sessions for a user."""
        return self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(desc(ChatSession.updated_at)).all()
    
    def find_by_user_and_session(self, user_id: int, session_id: str) -> Optional[ChatSession]:
        """Find a specific session for a user."""
        # Prefix session_id with user_id for uniqueness
        prefixed_session_id = f"{user_id}_{session_id}"
        return self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.id == prefixed_session_id
        ).first()
    
    def update_alias(self, user_id: int, session_id: str, alias: str) -> Optional[ChatSession]:
        """Update session alias for a specific user and session."""
        session = self.find_by_user_and_session(user_id, session_id)
        if session:
            session.alias = alias
            session.updated_at = datetime.datetime.now(datetime.timezone.utc)
            self.db.commit()
            self.db.refresh(session)
        return session
    
    def delete_by_id(self, user_id: int, session_id: str) -> bool:
        """Delete a session by ID."""
        # Prefix session_id with user_id for uniqueness
        prefixed_session_id = f"{user_id}_{session_id}"
        deleted_count = self.db.query(ChatSession).filter(
            ChatSession.id == prefixed_session_id
        ).delete()
        self.db.commit()
        return deleted_count > 0
    
    def get_sessions_with_message_count(self, user_id: int) -> List[tuple]:
        """Get sessions with message counts for a user."""
        result = self.db.query(
            ChatSession,
            func.count(ChatbotMessage.id).label('message_count')
        ).outerjoin(
            ChatbotMessage, ChatSession.id == ChatbotMessage.session_id
        ).filter(
            ChatSession.user_id == user_id
        ).group_by(
            ChatSession.id
        ).order_by(
            desc(ChatSession.updated_at)
        ).all()
        
        return result


def create_chat_session_repository(db: Session = Depends(get_database_session)) -> ChatSessionRepository:
    """Dependency injection function to create ChatSessionRepository instance."""
    return ChatSessionSqliteRepository(db)
