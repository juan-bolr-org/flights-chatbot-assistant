"""
Tests for User Router - Router Layer
Tests mock the service layer to focus on HTTP concerns using FastAPI dependency overrides.
"""

import pytest
import sys
import os
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import status

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from routers.users import router
from services.user import UserService, create_user_service
from schemas.user import Token, UserResponse
from exceptions import EmailAlreadyExistsError, InvalidCredentialsError
from fastapi import FastAPI


class TestUserRouter:
    """Test suite for User Router with mocked service layer using dependency overrides."""
    
    @pytest.fixture
    def mock_user_service(self):
        """Mock UserService for testing."""
        return Mock(spec=UserService)
    
    @pytest.fixture
    def app(self, mock_user_service):
        """Create FastAPI app with user router and dependency override."""
        app = FastAPI()
        app.include_router(router)
        
        # Override the dependency
        app.dependency_overrides[create_user_service] = lambda: mock_user_service
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_register_data(self):
        """Sample registration data."""
        return {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "secure_password123",
            "phone": "+1234567890"
        }
    
    @pytest.fixture
    def sample_login_data(self):
        """Sample login data."""
        return {
            "email": "john.doe@example.com",
            "password": "secure_password123"
        }
    
    @pytest.fixture
    def sample_token_response(self):
        """Sample token response."""
        return Token(access_token="test_access_token", token_type="bearer")
    
    @pytest.fixture
    def sample_user_response(self):
        """Sample user response."""
        from datetime import datetime, timezone
        return UserResponse(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            created_at=datetime.now(timezone.utc),
            token=Token(access_token="test_access_token", token_type="bearer")
        )
    
    # ===== REGISTRATION ENDPOINT TESTS =====
    
    def test_register_success(self, client, mock_user_service, sample_register_data, sample_token_response):
        """Test successful user registration."""
        # Setup mock
        mock_user_service.register.return_value = sample_token_response
        
        # Execute
        response = client.post("/users/register", json=sample_register_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_token"] == "test_access_token"
        assert data["token_type"] == "bearer"
        
        # Verify service was called
        mock_user_service.register.assert_called_once()
    
    def test_register_email_already_exists(self, client, mock_user_service, sample_register_data):
        """Test registration failure when email already exists."""
        # Setup mock
        mock_user_service.register.side_effect = EmailAlreadyExistsError("john.doe@example.com")
        
        # Execute
        response = client.post("/users/register", json=sample_register_data)
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "EMAIL_ALREADY_EXISTS"
        assert "Email already registered" in data["detail"]["message"]
        assert data["detail"]["details"]["email"] == "john.doe@example.com"
    
    def test_register_internal_error(self, client, mock_user_service, sample_register_data):
        """Test registration with unexpected internal error."""
        # Setup mock
        mock_user_service.register.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.post("/users/register", json=sample_register_data)
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error registering user" in data["detail"]
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email format."""
        invalid_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "password": "secure_password123",
            "phone": "+1234567890"
        }
        
        response = client.post("/users/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_required_fields(self, client):
        """Test registration with missing required fields."""
        invalid_data = {
            "name": "John Doe"
            # Missing email and password
        }
        
        response = client.post("/users/register", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_without_phone(self, client, mock_user_service):
        """Test registration without optional phone field."""
        data_without_phone = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "secure_password123"
        }
        
        mock_user_service.register.return_value = Token(
            access_token="test_token", 
            token_type="bearer"
        )
        
        response = client.post("/users/register", json=data_without_phone)
        assert response.status_code == status.HTTP_200_OK
    
    # ===== LOGIN ENDPOINT TESTS =====
    
    def test_login_success(self, client, mock_user_service, sample_login_data, sample_user_response):
        """Test successful user login."""
        # Setup mock
        mock_user_service.login.return_value = sample_user_response
        
        # Execute
        response = client.post("/users/login", json=sample_login_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "John Doe"
        assert data["email"] == "john.doe@example.com"
        assert data["phone"] == "+1234567890"
        assert data["token"]["access_token"] == "test_access_token"
        assert data["token"]["token_type"] == "bearer"
        
        # Verify service was called
        mock_user_service.login.assert_called_once()
    
    def test_login_invalid_credentials(self, client, mock_user_service, sample_login_data):
        """Test login failure with invalid credentials."""
        # Setup mock
        mock_user_service.login.side_effect = InvalidCredentialsError()
        
        # Execute
        response = client.post("/users/login", json=sample_login_data)
        
        # Verify
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"]["error_code"] == "INVALID_CREDENTIALS"
        assert "Incorrect email or password" in data["detail"]["message"]
    
    def test_login_internal_error(self, client, mock_user_service, sample_login_data):
        """Test login with unexpected internal error."""
        # Setup mock
        mock_user_service.login.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.post("/users/login", json=sample_login_data)
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error during login" in data["detail"]
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        invalid_data = {
            "email": "invalid-email",
            "password": "secure_password123"
        }
        
        response = client.post("/users/login", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_missing_password(self, client):
        """Test login with missing password."""
        invalid_data = {
            "email": "john.doe@example.com"
            # Missing password
        }
        
        response = client.post("/users/login", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        empty_data = {
            "email": "",
            "password": ""
        }
        
        response = client.post("/users/login", json=empty_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # ===== EDGE CASES =====
    
    def test_register_very_long_name(self, client, mock_user_service):
        """Test registration with very long name."""
        long_name_data = {
            "name": "A" * 1000,  # Very long name
            "email": "test@example.com",
            "password": "secure_password123"
        }
        
        mock_user_service.register.return_value = Token(
            access_token="test_token", 
            token_type="bearer"
        )
        
        response = client.post("/users/register", json=long_name_data)
        # Should still work (validation depends on your schema constraints)
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]
    
    def test_multiple_registrations_same_email(self, client, mock_user_service):
        """Test multiple registration attempts with same email."""
        data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "password": "secure_password123"
        }
        
        # First call succeeds
        mock_user_service.register.return_value = Token(
            access_token="test_token", 
            token_type="bearer"
        )
        response1 = client.post("/users/register", json=data)
        assert response1.status_code == status.HTTP_200_OK
        
        # Second call fails - reset the mock for different behavior
        mock_user_service.register.side_effect = EmailAlreadyExistsError("john.doe@example.com")
        response2 = client.post("/users/register", json=data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
