from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import datetime
from fastapi import Depends
from resources.database import get_database_session
from models import ChatbotMessage


class ChatbotMessageRepository(ABC):
    """Abstract base class for ChatbotMessage repository operations."""
    
    @abstractmethod
    def create(self, user_id: int, session_id: str, message: str, response: str) -> ChatbotMessage:
        """Create a new chatbot message with session ID."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int, limit: int = 50, offset: int = 0) -> List[ChatbotMessage]:
        """Find chatbot messages for a user with pagination."""
        pass
    
    @abstractmethod
    def find_by_user_id_and_session(self, user_id: int, session_id: str, limit: int = 50, offset: int = 0) -> List[ChatbotMessage]:
        """Find chatbot messages for a user and session with pagination."""
        pass
    
    @abstractmethod
    def count_by_user_id(self, user_id: int) -> int:
        """Count total chatbot messages for a user."""
        pass
    
    @abstractmethod
    def count_by_user_id_and_session(self, user_id: int, session_id: str) -> int:
        """Count total chatbot messages for a user and session."""
        pass
    
    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> int:
        """Delete all chatbot messages for a user. Returns count of deleted messages."""
        pass
    
    @abstractmethod
    def delete_by_user_id_and_session(self, user_id: int, session_id: str) -> int:
        """Delete all chatbot messages for a user and session. Returns count of deleted messages."""
        pass
    
    @abstractmethod
    def get_user_sessions(self, user_id: int) -> List[str]:
        """Get all unique session IDs for a user."""
        pass


class ChatbotMessageSqliteRepository(ChatbotMessageRepository):
    """SQLite implementation of ChatbotMessageRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, session_id: str, message: str, response: str) -> ChatbotMessage:
        """Create a new chatbot message with session ID."""
        chat_message = ChatbotMessage(
            user_id=user_id,
            session_id=session_id,
            user_message=message,
            bot_response=response,
            created_at=datetime.datetime.now(datetime.UTC)
        )
        self.db.add(chat_message)
        self.db.commit()
        self.db.refresh(chat_message)
        return chat_message
    
    def find_by_user_id(self, user_id: int, limit: int = 50, offset: int = 0) -> List[ChatbotMessage]:
        """Find chatbot messages for a user with pagination."""
        return self.db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user_id
        ).order_by(
            ChatbotMessage.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    def find_by_user_id_and_session(self, user_id: int, session_id: str, limit: int = 50, offset: int = 0) -> List[ChatbotMessage]:
        """Find chatbot messages for a user and session with pagination."""
        return self.db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user_id,
            ChatbotMessage.session_id == session_id
        ).order_by(
            ChatbotMessage.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    def count_by_user_id(self, user_id: int) -> int:
        """Count total chatbot messages for a user."""
        return self.db.query(ChatbotMessage).filter(ChatbotMessage.user_id == user_id).count()
    
    def count_by_user_id_and_session(self, user_id: int, session_id: str) -> int:
        """Count total chatbot messages for a user and session."""
        return self.db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user_id,
            ChatbotMessage.session_id == session_id
        ).count()
    
    def delete_by_user_id(self, user_id: int) -> int:
        """Delete all chatbot messages for a user. Returns count of deleted messages."""
        deleted_count = self.db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user_id
        ).delete()
        self.db.commit()
        return deleted_count
    
    def delete_by_user_id_and_session(self, user_id: int, session_id: str) -> int:
        """Delete all chatbot messages for a user and session. Returns count of deleted messages."""
        deleted_count = self.db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user_id,
            ChatbotMessage.session_id == session_id
        ).delete()
        self.db.commit()
        return deleted_count
    
    def get_user_sessions(self, user_id: int) -> List[str]:
        """Get all unique session IDs for a user."""
        result = self.db.query(ChatbotMessage.session_id).filter(
            ChatbotMessage.user_id == user_id
        ).distinct().all()
        return [row[0] for row in result]


def create_chatbot_message_repository(db: Session = Depends(get_database_session)) -> ChatbotMessageRepository:
    """Dependency injection function to create ChatbotMessageRepository instance."""
    return ChatbotMessageSqliteRepository(db)
