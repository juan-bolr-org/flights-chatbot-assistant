"""
Tests for ChatbotMessageRepository - Repository Layer
Tests use in-memory SQLite database to ensure data isolation.
"""

import pytest
import sys
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Base, ChatbotMessage, User
from repository.chatbot_message import ChatbotMessageSqliteRepository


class TestChatbotMessageRepository:
    """Test suite for ChatbotMessageRepository using in-memory SQLite database."""
    
    @pytest.fixture
    def db_session(self):
        """Create an in-memory SQLite database session for testing."""
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture
    def message_repo(self, db_session):
        """Create a ChatbotMessageRepository instance with test database."""
        return ChatbotMessageSqliteRepository(db_session)
    
    @pytest.fixture
    def sample_user(self, db_session):
        """Create a sample user for testing."""
        user = User(
            name="Test User",
            email="test@example.com",
            password_hash="hashed_password",
            phone="1234567890"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def sample_message_data(self):
        """Sample message data for testing."""
        return {
            "message": "What flights are available?",
            "response": "There are several flights available..."
        }

    # ===== POSITIVE TESTS =====
    
    def test_create_message_success(self, message_repo, sample_user, sample_message_data):
        """Test successful message creation."""
        message = message_repo.create(
            user_id=sample_user.id,
            message=sample_message_data["message"],
            response=sample_message_data["response"]
        )
        
        assert message.id is not None
        assert message.user_id == sample_user.id
        assert message.user_message == sample_message_data["message"]
        assert message.bot_response == sample_message_data["response"]
        assert message.created_at is not None
        assert message.session_id == f"chat_session_{sample_user.id}"

    def test_find_by_user_id_success(self, message_repo, sample_user, sample_message_data):
        """Test finding messages by user ID."""
        # Create multiple messages
        message1 = message_repo.create(
            user_id=sample_user.id,
            message=sample_message_data["message"],
            response=sample_message_data["response"]
        )
        message2 = message_repo.create(
            user_id=sample_user.id,
            message="Segunda pregunta",
            response="Segunda respuesta"
        )
        
        messages = message_repo.find_by_user_id(sample_user.id)
        
        assert len(messages) == 2
        # Verify that messages are ordered by created_at desc
        assert messages[0].id == message2.id
        assert messages[1].id == message1.id

    def test_count_by_user_id_success(self, message_repo, sample_user, sample_message_data):
        """Test counting messages for a user."""
        message_repo.create(
            user_id=sample_user.id,
            message=sample_message_data["message"],
            response=sample_message_data["response"]
        )
        message_repo.create(
            user_id=sample_user.id,
            message="Segunda pregunta",
            response="Segunda respuesta"
        )
        
        count = message_repo.count_by_user_id(sample_user.id)
        assert count == 2

    def test_delete_by_user_id_success(self, message_repo, sample_user, sample_message_data):
        """Test deleting all messages for a user."""
        message_repo.create(
            user_id=sample_user.id,
            message=sample_message_data["message"],
            response=sample_message_data["response"]
        )
        message_repo.create(
            user_id=sample_user.id,
            message="Segunda pregunta",
            response="Segunda respuesta"
        )
        
        deleted_count = message_repo.delete_by_user_id(sample_user.id)
        assert deleted_count == 2
        
        # Verify messages were deleted
        messages = message_repo.find_by_user_id(sample_user.id)
        assert len(messages) == 0

    # ===== PAGINATION TESTS =====

    def test_find_by_user_id_with_pagination(self, message_repo, sample_user, sample_message_data):
        """Test message pagination."""
        # Create 3 messages
        for i in range(3):
            message_repo.create(
                user_id=sample_user.id,
                message=f"Message {i}",
                response=f"Response {i}"
            )
        
        # Test limit
        messages = message_repo.find_by_user_id(sample_user.id, limit=2)
        assert len(messages) == 2
        
        # Test offset
        messages = message_repo.find_by_user_id(sample_user.id, limit=2, offset=1)
        assert len(messages) == 2
        assert messages[0].user_message == 'Message 1'

    # ===== NEGATIVE TESTS =====

    def test_find_by_user_id_no_messages(self, message_repo, sample_user):
        """Test finding messages when user has none."""
        messages = message_repo.find_by_user_id(sample_user.id)
        assert len(messages) == 0

    def test_count_by_user_id_no_messages(self, message_repo, sample_user):
        """Test counting messages when user has none."""
        count = message_repo.count_by_user_id(sample_user.id)
        assert count == 0

    def test_delete_by_user_id_no_messages(self, message_repo, sample_user):
        """Test deleting messages when user has none."""
        deleted_count = message_repo.delete_by_user_id(sample_user.id)
        assert deleted_count == 0

    # ===== EDGE CASES =====

    def test_create_message_long_content(self, message_repo, sample_user):
        """Test creating message with long content."""
        long_message = "A" * 1000  # 1000 character message
        long_response = "B" * 1000  # 1000 character response
        
        message = message_repo.create(
            user_id=sample_user.id,
            message=long_message,
            response=long_response
        )
        
        assert message.user_message == long_message
        assert message.bot_response == long_response

    def test_messages_from_multiple_users(self, message_repo, db_session, sample_user):
        """Test messages are properly isolated between users."""
        # Create second user
        user2 = User(
            name="Test User 2",
            email="test2@example.com",
            password_hash="hashed_password",
            phone="0987654321"
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)
        
        # Create message for first user
        message_repo.create(
            user_id=sample_user.id,
            message="Mensaje usuario 1",
            response="Respuesta usuario 1"
        )
        
        # Create message for second user
        message_repo.create(
            user_id=user2.id,
            message="Mensaje usuario 2",
            response="Respuesta usuario 2"
        )
        
        # Check messages are isolated
        user1_messages = message_repo.find_by_user_id(sample_user.id)
        user2_messages = message_repo.find_by_user_id(user2.id)
        
        assert len(user1_messages) == 1
        assert len(user2_messages) == 1
        assert user1_messages[0].user_message == "Mensaje usuario 1"
        assert user2_messages[0].user_message == "Mensaje usuario 2"