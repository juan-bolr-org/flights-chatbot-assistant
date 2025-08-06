"""
Tests for UserService - Service Layer
Tests mock the repository layer to focus on business logic.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.user import UserBusinessService
from repository.user import UserRepository
from models import User
from resources.crypto import CryptoManager
from schemas.user import UserCreate, UserLogin, Token, UserResponse
from exceptions import EmailAlreadyExistsError, InvalidCredentialsError


class TestUserService:
    """Test suite for UserService with mocked dependencies."""
    
    @pytest.fixture
    def mock_user_repo(self):
        """Mock UserRepository for testing."""
        return Mock(spec=UserRepository)
    
    @pytest.fixture
    def mock_crypto(self):
        """Mock CryptoManager for testing."""
        mock = Mock(spec=CryptoManager)
        mock.get_password_hash.return_value = "hashed_password_123"
        mock.verify_password.return_value = True
        mock.create_access_token.return_value = "test_access_token_123"
        
        # Mock the config object with access_token_expire_minutes
        mock_config = Mock()
        mock_config.access_token_expire_minutes = 30
        mock.config = mock_config
        
        return mock
    
    @pytest.fixture
    def user_service(self, mock_user_repo, mock_crypto):
        """Create UserService instance with mocked dependencies."""
        return UserBusinessService(mock_user_repo, mock_crypto)
    
    @pytest.fixture
    def sample_user_create(self):
        """Sample UserCreate schema for testing."""
        return UserCreate(
            name="John Doe",
            email="john.doe@example.com",
            password="secure_password123",
            phone="+1234567890"
        )
    
    @pytest.fixture
    def sample_user_login(self):
        """Sample UserLogin schema for testing."""
        return UserLogin(
            email="john.doe@example.com",
            password="secure_password123"
        )
    
    @pytest.fixture
    def sample_db_user(self):
        """Sample User model instance for testing."""
        return User(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password_123",
            phone="+1234567890",
            created_at=datetime.now(timezone.utc),
            token_expiration=datetime.now(timezone.utc) + timedelta(hours=1)
        )
    
    # ===== REGISTRATION TESTS =====
    
    def test_register_success(self, user_service, mock_user_repo, mock_crypto, sample_user_create, sample_db_user):
        """Test successful user registration."""
        # Setup mocks
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.create.return_value = sample_db_user
        
        # Execute
        result = user_service.register(sample_user_create)
        
        # Verify
        assert isinstance(result, Token)
        assert result.access_token == "test_access_token_123"
        assert result.token_type == "bearer"
        
        # Verify repository calls
        mock_user_repo.exists_by_email.assert_called_once_with("john.doe@example.com")
        mock_user_repo.create.assert_called_once_with(
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password_123",
            phone="+1234567890"
        )
        
        # Verify crypto calls
        mock_crypto.get_password_hash.assert_called_once_with("secure_password123")
        # Check that create_access_token was called with both data and expires_delta
        mock_crypto.create_access_token.assert_called_once()
        call_args = mock_crypto.create_access_token.call_args
        assert call_args.kwargs['data'] == {"sub": "john.doe@example.com"}
        assert call_args.kwargs['expires_delta'] == timedelta(minutes=30)
    
    def test_register_email_already_exists(self, user_service, mock_user_repo, sample_user_create):
        """Test registration failure when email already exists."""
        # Setup mock
        mock_user_repo.exists_by_email.return_value = True
        
        # Execute and verify exception
        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            user_service.register(sample_user_create)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "EMAIL_ALREADY_EXISTS"
        assert exc_info.value.details["email"] == "john.doe@example.com"
        
        # Verify repository calls
        mock_user_repo.exists_by_email.assert_called_once_with("john.doe@example.com")
        mock_user_repo.create.assert_not_called()
    
    def test_register_without_phone(self, user_service, mock_user_repo, mock_crypto, sample_db_user):
        """Test registration without phone number."""
        # Setup
        user_create = UserCreate(
            name="John Doe",
            email="john.doe@example.com",
            password="secure_password123"
        )
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.create.return_value = sample_db_user
        
        # Execute
        result = user_service.register(user_create)
        
        # Verify
        assert isinstance(result, Token)
        mock_user_repo.create.assert_called_once_with(
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password_123",
            phone=None
        )
    
    # ===== LOGIN TESTS =====
    
    def test_login_success(self, user_service, mock_user_repo, mock_crypto, sample_user_login, sample_db_user):
        """Test successful user login."""
        # Setup mocks
        mock_user_repo.find_by_email.return_value = sample_db_user
        mock_user_repo.update_token_expiration.return_value = sample_db_user
        mock_crypto.verify_password.return_value = True
        
        # Execute
        result = user_service.login(sample_user_login)
        
        # Verify
        assert isinstance(result, UserResponse)
        assert result.id == 1
        assert result.name == "John Doe"
        assert result.email == "john.doe@example.com"
        assert result.phone == "+1234567890"
        assert isinstance(result.token, Token)
        assert result.token.access_token == "test_access_token_123"
        
        # Verify repository calls
        mock_user_repo.find_by_email.assert_called_once_with("john.doe@example.com")
        mock_user_repo.update_token_expiration.assert_called_once()
        
        # Verify crypto calls
        mock_crypto.verify_password.assert_called_once_with("secure_password123", "hashed_password_123")
        # Check that create_access_token was called with both data and expires_delta
        mock_crypto.create_access_token.assert_called_once()
        call_args = mock_crypto.create_access_token.call_args
        assert call_args.kwargs['data'] == {"sub": "john.doe@example.com"}
        assert call_args.kwargs['expires_delta'] == timedelta(minutes=30)
    
    def test_login_user_not_found(self, user_service, mock_user_repo, sample_user_login):
        """Test login failure when user doesn't exist."""
        # Setup mock
        mock_user_repo.find_by_email.return_value = None
        
        # Execute and verify exception
        with pytest.raises(InvalidCredentialsError) as exc_info:
            user_service.login(sample_user_login)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "INVALID_CREDENTIALS"
        assert "Incorrect email or password" in exc_info.value.message
        
        # Verify repository calls
        mock_user_repo.find_by_email.assert_called_once_with("john.doe@example.com")
        mock_user_repo.update_token_expiration.assert_not_called()
    
    def test_login_wrong_password(self, user_service, mock_user_repo, mock_crypto, sample_user_login, sample_db_user):
        """Test login failure with wrong password."""
        # Setup mocks
        mock_user_repo.find_by_email.return_value = sample_db_user
        mock_crypto.verify_password.return_value = False
        
        # Execute and verify exception
        with pytest.raises(InvalidCredentialsError) as exc_info:
            user_service.login(sample_user_login)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "INVALID_CREDENTIALS"
        
        # Verify calls
        mock_user_repo.find_by_email.assert_called_once_with("john.doe@example.com")
        mock_crypto.verify_password.assert_called_once_with("secure_password123", "hashed_password_123")
        mock_user_repo.update_token_expiration.assert_not_called()
    
    def test_login_empty_password(self, user_service, mock_user_repo, sample_db_user):
        """Test login with empty password."""
        # Setup
        login_data = UserLogin(email="john.doe@example.com", password="")
        mock_user_repo.find_by_email.return_value = sample_db_user
        
        # Execute and verify exception
        with pytest.raises(InvalidCredentialsError):
            user_service.login(login_data)
    
    # ===== EDGE CASES =====
    
    def test_login_token_expiration_update(self, user_service, mock_user_repo, mock_crypto, sample_user_login, sample_db_user):
        """Test that login updates token expiration correctly."""
        # Setup mocks
        mock_user_repo.find_by_email.return_value = sample_db_user
        mock_user_repo.update_token_expiration.return_value = sample_db_user
        mock_crypto.verify_password.return_value = True
        
        # Execute
        user_service.login(sample_user_login)
        
        # Verify token expiration was updated
        mock_user_repo.update_token_expiration.assert_called_once()
        call_args = mock_user_repo.update_token_expiration.call_args
        user_id, expiration = call_args[0]
        
        assert user_id == 1
        # Check that expiration is approximately 30 minutes in the future
        now = datetime.now(timezone.utc)
        assert expiration > now + timedelta(minutes=25)
        assert expiration < now + timedelta(minutes=35)
    
    def test_register_crypto_integration(self, user_service, mock_user_repo, sample_user_create, sample_db_user):
        """Test that registration properly integrates with crypto manager."""
        # Setup mocks
        mock_user_repo.exists_by_email.return_value = False
        mock_user_repo.create.return_value = sample_db_user
        
        # Execute
        user_service.register(sample_user_create)
        
        # Verify that password was hashed and token was created
        assert user_service.crypto.get_password_hash.called
        assert user_service.crypto.create_access_token.called
        
        # Verify the actual password that was hashed
        hash_call_args = user_service.crypto.get_password_hash.call_args[0]
        assert hash_call_args[0] == "secure_password123"
        
        # Verify token creation with correct subject
        token_call_args = user_service.crypto.create_access_token.call_args[1]
        assert token_call_args["data"]["sub"] == "john.doe@example.com"
