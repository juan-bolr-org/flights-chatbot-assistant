"""
Test for JWT Authentication Middleware
Tests the middleware validation logic and integration.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Request, Response
from fastapi.testclient import TestClient

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from middleware.auth import JWTAuthMiddleware
from resources.crypto import crypto_manager
from models import User

class TestJWTAuthMiddleware:
    """Test class for JWT Authentication Middleware"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.middleware = JWTAuthMiddleware(
            app=None,
            excluded_paths=["/health", "/docs", "/users/login"]
        )
        
        # Mock user for testing
        self.mock_user = Mock(spec=User)
        self.mock_user.id = 1
        self.mock_user.email = "test@example.com"
        self.mock_user.name = "Test User"
    
    def test_excluded_paths(self):
        """Test that excluded paths are correctly identified"""
        excluded_paths = ["/health", "/docs", "/users/login", "/public/*"]
        middleware = JWTAuthMiddleware(app=None, excluded_paths=excluded_paths)
        
        # Test exact matches
        assert middleware._is_path_excluded("/health") == True
        assert middleware._is_path_excluded("/docs") == True
        assert middleware._is_path_excluded("/users/login") == True
        
        # Test wildcard matches
        assert middleware._is_path_excluded("/public/anything") == True
        assert middleware._is_path_excluded("/public/test/nested") == True
        
        # Test non-excluded paths
        assert middleware._is_path_excluded("/users/me") == False
        assert middleware._is_path_excluded("/flights") == False
    
    def test_extract_token_from_header(self):
        """Test token extraction from Authorization header"""
        # Mock request with Authorization header
        request = Mock(spec=Request)
        request.headers = {"Authorization": "Bearer test_token_123"}
        request.cookies = {}
        
        token = self.middleware._extract_token(request)
        assert token == "test_token_123"
    
    def test_extract_token_from_cookie(self):
        """Test token extraction from cookies"""
        # Mock request with cookie
        request = Mock(spec=Request)
        request.headers = {}
        request.cookies = {"access_token": "cookie_token_456"}
        
        token = self.middleware._extract_token(request)
        assert token == "cookie_token_456"
    
    def test_extract_token_header_priority(self):
        """Test that Authorization header takes priority over cookies"""
        # Mock request with both header and cookie
        request = Mock(spec=Request)
        request.headers = {"Authorization": "Bearer header_token"}
        request.cookies = {"access_token": "cookie_token"}
        
        token = self.middleware._extract_token(request)
        assert token == "header_token"
    
    def test_extract_token_no_token(self):
        """Test token extraction when no token is present"""
        request = Mock(spec=Request)
        request.headers = {}
        request.cookies = {}
        
        token = self.middleware._extract_token(request)
        assert token is None
    
    def test_extract_token_invalid_header_format(self):
        """Test token extraction with invalid Authorization header format"""
        request = Mock(spec=Request)
        request.headers = {"Authorization": "Invalid format"}
        request.cookies = {}
        
        token = self.middleware._extract_token(request)
        assert token is None
    
    @pytest.mark.asyncio
    async def test_validate_token_and_get_user_success(self):
        """Test successful token validation and user retrieval"""
        # Create a real token for testing
        token_data = {"sub": self.mock_user.email}
        test_token = crypto_manager.create_access_token(token_data)
        
        # Mock database session and repository
        with patch('middleware.auth.get_database_session') as mock_get_db, \
             patch('middleware.auth.UserSqliteRepository') as mock_repo_class:
            
            # Setup mock database session
            mock_session = Mock()
            mock_get_db.return_value = iter([mock_session])
            
            # Setup mock repository
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.find_by_email.return_value = self.mock_user
            
            # Test the validation
            result = await self.middleware._validate_token_and_get_user(test_token)
            
            # Assertions
            assert result == self.mock_user
            mock_repo.find_by_email.assert_called_once_with(self.mock_user.email)
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_token_invalid(self):
        """Test validation with invalid token"""
        invalid_token = "invalid.token.here"
        
        result = await self.middleware._validate_token_and_get_user(invalid_token)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_validate_token_user_not_found(self):
        """Test validation when user is not found in database"""
        # Create a valid token
        token_data = {"sub": "nonexistent@example.com"}
        test_token = crypto_manager.create_access_token(token_data)
        
        with patch('middleware.auth.get_database_session') as mock_get_db, \
             patch('middleware.auth.UserSqliteRepository') as mock_repo_class:
            
            mock_session = Mock()
            mock_get_db.return_value = iter([mock_session])
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.find_by_email.return_value = None  # User not found
            
            result = await self.middleware._validate_token_and_get_user(test_token)
            
            assert result is None
            mock_session.close.assert_called_once()
    
    def test_create_unauthorized_response(self):
        """Test creation of unauthorized response"""
        response = self.middleware._create_unauthorized_response("Test message")
        
        assert response.status_code == 401
        assert response.media_type == "application/json"
        assert '"detail": "Test message"' in response.body.decode()
    
    def test_create_error_response(self):
        """Test creation of error response"""
        response = self.middleware._create_error_response(500, "Server error")
        
        assert response.status_code == 500
        assert response.media_type == "application/json"
        assert '"detail": "Server error"' in response.body.decode()
    
    @pytest.mark.asyncio
    async def test_dispatch_excluded_path(self):
        """Test middleware dispatch for excluded paths"""
        # Mock request for excluded path
        request = Mock(spec=Request)
        request.url.path = "/health"
        
        # Mock call_next
        call_next = AsyncMock()
        expected_response = Mock(spec=Response)
        call_next.return_value = expected_response
        
        # Test dispatch
        result = await self.middleware.dispatch(request, call_next)
        
        # Assertions
        assert result == expected_response
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_dispatch_no_token(self):
        """Test middleware dispatch when no token is provided"""
        # Mock request for protected path with no token
        request = Mock(spec=Request)
        request.url.path = "/users/me"
        request.headers = {}
        request.cookies = {}
        
        call_next = AsyncMock()
        
        # Test dispatch
        result = await self.middleware.dispatch(request, call_next)
        
        # Assertions
        assert result.status_code == 401
        assert '"No authentication token provided"' in result.body.decode()
        call_next.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_dispatch_success(self):
        """Test successful middleware dispatch with valid token"""
        # Create valid token
        token_data = {"sub": self.mock_user.email}
        test_token = crypto_manager.create_access_token(token_data)
        
        # Mock request
        request = Mock(spec=Request)
        request.url.path = "/users/me"
        request.headers = {"Authorization": f"Bearer {test_token}"}
        request.cookies = {}
        request.state = Mock()
        
        # Mock call_next
        call_next = AsyncMock()
        expected_response = Mock(spec=Response)
        call_next.return_value = expected_response
        
        # Mock database operations
        with patch('middleware.auth.get_database_session') as mock_get_db, \
             patch('middleware.auth.UserSqliteRepository') as mock_repo_class:
            
            mock_session = Mock()
            mock_get_db.return_value = iter([mock_session])
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.find_by_email.return_value = self.mock_user
            
            # Test dispatch
            result = await self.middleware.dispatch(request, call_next)
            
            # Assertions
            assert result == expected_response
            assert request.state.current_user == self.mock_user
            assert request.state.jwt_token == test_token
            call_next.assert_called_once_with(request)


def test_crypto_manager_token_validation():
    """Test the crypto manager's token validation directly"""
    # Test valid token creation and validation
    email = "test@example.com"
    token_data = {"sub": email}
    
    # Create token
    token = crypto_manager.create_access_token(token_data)
    assert token is not None
    assert isinstance(token, str)
    
    # Validate token
    extracted_email = crypto_manager.get_token_subject(token)
    assert extracted_email == email
    
    # Test invalid token
    invalid_email = crypto_manager.get_token_subject("invalid.token")
    assert invalid_email is None


if __name__ == "__main__":
    # Run tests directly if executed as script
    pytest.main([__file__, "-v"])
