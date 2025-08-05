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
    def create(self, user_id: int, message: str, response: str) -> ChatbotMessage:
        """Create a new chatbot message."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int, limit: int = 50, offset: int = 0) -> List[ChatbotMessage]:
        """Find chatbot messages for a user with pagination."""
        pass
    
    @abstractmethod
    def count_by_user_id(self, user_id: int) -> int:
        """Count total chatbot messages for a user."""
        pass
    
    @abstractmethod
    def delete_by_user_id(self, user_id: int) -> int:
        """Delete all chatbot messages for a user. Returns count of deleted messages."""
        pass


class ChatbotMessageSqliteRepository(ChatbotMessageRepository):
    """SQLite implementation of ChatbotMessageRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, message: str, response: str) -> ChatbotMessage:
        """Create a new chatbot message."""
        chat_message = ChatbotMessage(
            user_id=user_id,
            session_id=f"chat_session_{user_id}",
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
    
    def count_by_user_id(self, user_id: int) -> int:
        """Count total chatbot messages for a user."""
        return self.db.query(ChatbotMessage).filter(ChatbotMessage.user_id == user_id).count()
    
    def delete_by_user_id(self, user_id: int) -> int:
        """Delete all chatbot messages for a user. Returns count of deleted messages."""
        deleted_count = self.db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user_id
        ).delete()
        self.db.commit()
        return deleted_count


def create_chatbot_message_repository(db: Session = Depends(get_database_session)) -> ChatbotMessageRepository:
    """Dependency injection function to create ChatbotMessageRepository instance."""
    return ChatbotMessageSqliteRepository(db)
