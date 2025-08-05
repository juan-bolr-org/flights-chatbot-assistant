"""
Tests for UserRepository - Repository Layer
Tests use in-memory SQLite database to ensure data isolation.
"""

import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Base, User
from repository.user import UserSqliteRepository


class TestUserRepository:
    """Test suite for UserRepository using in-memory SQLite database."""
    
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
    def user_repo(self, db_session):
        """Create a UserRepository instance with test database."""
        return UserSqliteRepository(db_session)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password_hash": "hashed_password_123",
            "phone": "+1234567890"
        }
    
    # ===== POSITIVE TESTS =====
    
    def test_create_user_success(self, user_repo, sample_user_data):
        """Test successful user creation."""
        user = user_repo.create(**sample_user_data)
        
        assert user.id is not None
        assert user.name == sample_user_data["name"]
        assert user.email == sample_user_data["email"]
        assert user.password_hash == sample_user_data["password_hash"]
        assert user.phone == sample_user_data["phone"]
        assert user.created_at is not None
        assert user.token_expiration is not None
        
        # Check that token expiration is set to future (around 1 hour)
        now = datetime.now(timezone.utc)
        
        # Handle timezone differences - if token_expiration is naive, assume UTC
        token_exp = user.token_expiration
        if token_exp.tzinfo is None:
            token_exp = token_exp.replace(tzinfo=timezone.utc)
        
        assert token_exp > now
        assert token_exp < now + timedelta(hours=2)
    
    def test_create_user_without_phone(self, user_repo, sample_user_data):
        """Test user creation without phone number."""
        del sample_user_data["phone"]
        user = user_repo.create(**sample_user_data)
        
        assert user.id is not None
        assert user.phone is None
        assert user.name == sample_user_data["name"]
        assert user.email == sample_user_data["email"]
    
    def test_find_by_email_success(self, user_repo, sample_user_data):
        """Test finding user by email when user exists."""
        created_user = user_repo.create(**sample_user_data)
        found_user = user_repo.find_by_email(sample_user_data["email"])
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == sample_user_data["email"]
    
    def test_find_by_id_success(self, user_repo, sample_user_data):
        """Test finding user by ID when user exists."""
        created_user = user_repo.create(**sample_user_data)
        found_user = user_repo.find_by_id(created_user.id)
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == sample_user_data["email"]
    
    def test_exists_by_email_true(self, user_repo, sample_user_data):
        """Test email existence check when user exists."""
        user_repo.create(**sample_user_data)
        exists = user_repo.exists_by_email(sample_user_data["email"])
        
        assert exists is True
    
    def test_update_token_expiration_success(self, user_repo, sample_user_data):
        """Test successful token expiration update."""
        user = user_repo.create(**sample_user_data)
        new_expiration = datetime.now(timezone.utc) + timedelta(hours=2)
        
        updated_user = user_repo.update_token_expiration(user.id, new_expiration)
        
        assert updated_user.id == user.id
        
        # Handle timezone differences - if token_expiration is naive, assume UTC
        actual_expiration = updated_user.token_expiration
        if actual_expiration.tzinfo is None:
            actual_expiration = actual_expiration.replace(tzinfo=timezone.utc)
        
        assert actual_expiration == new_expiration
    
    def test_find_expired_tokens(self, user_repo, sample_user_data):
        """Test finding users with expired tokens."""
        # Create user with expired token
        user = user_repo.create(**sample_user_data)
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)
        user_repo.update_token_expiration(user.id, past_time)
        
        # Create user with valid token
        sample_user_data["email"] = "another@example.com"
        user_repo.create(**sample_user_data)
        
        expired_users = user_repo.find_expired_tokens()
        
        assert len(expired_users) == 1
        assert expired_users[0].email == "john.doe@example.com"
    
    # ===== NEGATIVE TESTS =====
    
    def test_find_by_email_not_found(self, user_repo):
        """Test finding user by email when user doesn't exist."""
        found_user = user_repo.find_by_email("nonexistent@example.com")
        assert found_user is None
    
    def test_find_by_id_not_found(self, user_repo):
        """Test finding user by ID when user doesn't exist."""
        found_user = user_repo.find_by_id(999)
        assert found_user is None
    
    def test_exists_by_email_false(self, user_repo):
        """Test email existence check when user doesn't exist."""
        exists = user_repo.exists_by_email("nonexistent@example.com")
        assert exists is False
    
    def test_update_token_expiration_user_not_found(self, user_repo):
        """Test token expiration update when user doesn't exist."""
        new_expiration = datetime.now(timezone.utc) + timedelta(hours=2)
        
        with pytest.raises(ValueError, match="User with ID 999 not found"):
            user_repo.update_token_expiration(999, new_expiration)
    
    def test_find_expired_tokens_empty(self, user_repo, sample_user_data):
        """Test finding expired tokens when no users have expired tokens."""
        # Create user with future token expiration
        user_repo.create(**sample_user_data)
        
        expired_users = user_repo.find_expired_tokens()
        assert len(expired_users) == 0
    
    # ===== EDGE CASES =====
    
    def test_create_multiple_users_different_emails(self, user_repo, sample_user_data):
        """Test creating multiple users with different emails."""
        user1 = user_repo.create(**sample_user_data)
        
        sample_user_data["email"] = "another@example.com"
        sample_user_data["name"] = "Jane Doe"
        user2 = user_repo.create(**sample_user_data)
        
        assert user1.id != user2.id
        assert user1.email != user2.email
    
    def test_token_expiration_precision(self, user_repo, sample_user_data):
        """Test that token expiration is stored with proper precision."""
        user = user_repo.create(**sample_user_data)
        
        # Test updating with microsecond precision
        precise_time = datetime.now(timezone.utc).replace(microsecond=123456)
        updated_user = user_repo.update_token_expiration(user.id, precise_time)
        
        # SQLite might not preserve full microsecond precision, so we check seconds
        # Also handle timezone differences by normalizing both to UTC
        expected_time = precise_time.replace(microsecond=0)
        actual_time = updated_user.token_expiration
        
        # If actual_time is naive, assume it's UTC
        if actual_time.tzinfo is None:
            actual_time = actual_time.replace(tzinfo=timezone.utc)
        
        actual_time = actual_time.replace(microsecond=0)
        assert actual_time == expected_time
