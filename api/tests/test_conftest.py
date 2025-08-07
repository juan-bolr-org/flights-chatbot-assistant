"""
Tests for test configuration and fixtures.
"""
import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session

# Add src to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestConftest:
    """Test suite for conftest fixtures."""
    
    def test_in_memory_db_fixture(self, in_memory_db):
        """Test that in_memory_db fixture creates a working database session."""
        assert isinstance(in_memory_db, Session)
        
        # Test that we can execute a simple query
        from sqlalchemy import text
        result = in_memory_db.execute(text("SELECT 1 as test_value"))
        row = result.fetchone()
        assert row[0] == 1
    
    def test_crypto_manager_fixture(self, crypto_manager):
        """Test that crypto_manager fixture is properly initialized."""
        assert crypto_manager.is_initialized() is True
        
        # Test password hashing
        password = "test_password_123"
        hashed = crypto_manager.get_password_hash(password)
        assert hashed != password
        assert len(hashed) > 20  # Hashed passwords should be longer
        
        # Test password verification
        assert crypto_manager.verify_password(password, hashed) is True
        assert crypto_manager.verify_password("wrong_password", hashed) is False
    
    def test_mock_crypto_manager_fixture(self, mock_crypto_manager):
        """Test that mock_crypto_manager fixture has expected behavior."""
        # Test that it's a mock with the expected return values
        assert mock_crypto_manager.get_password_hash("any_password") == "hashed_password"
        assert mock_crypto_manager.verify_password("any_password", "any_hash") is True
        assert mock_crypto_manager.create_access_token({"sub": "test"}) == "test_access_token"
        assert mock_crypto_manager.is_initialized() is True
    
    def test_test_client_fixture(self, test_client):
        """Test that test_client fixture creates a working FastAPI test client."""
        # Test that the client can make requests
        response = test_client.get("/")
        # The exact status code depends on your app's root endpoint
        # We just want to ensure the client is working
        assert response.status_code in [200, 404, 422]  # Any valid HTTP response
    
    def test_test_user_data_fixture(self, test_user_data):
        """Test that test_user_data fixture has expected structure."""
        required_fields = ["name", "email", "password", "phone"]
        for field in required_fields:
            assert field in test_user_data
            assert test_user_data[field] is not None
        
        # Validate specific values
        assert test_user_data["name"] == "John Doe"
        assert test_user_data["email"] == "john.doe@example.com"
        assert test_user_data["password"] == "secure_password123"
        assert test_user_data["phone"] == "+1234567890"
    
    def test_test_login_data_fixture(self, test_login_data):
        """Test that test_login_data fixture has expected structure."""
        required_fields = ["email", "password"]
        for field in required_fields:
            assert field in test_login_data
            assert test_login_data[field] is not None
        
        # Validate specific values
        assert test_login_data["email"] == "john.doe@example.com"
        assert test_login_data["password"] == "secure_password123"
    
    def test_test_flight_data_fixture(self, test_flight_data):
        """Test that test_flight_data fixture has expected structure."""
        required_fields = ["origin", "destination", "departure_time", "arrival_time", "airline", "price", "status"]
        for field in required_fields:
            assert field in test_flight_data
            assert test_flight_data[field] is not None
        
        # Validate specific values
        assert test_flight_data["origin"] == "New York"
        assert test_flight_data["destination"] == "Los Angeles"
        assert test_flight_data["airline"] == "American Airlines"
        assert test_flight_data["price"] == 299
        assert test_flight_data["status"] == "scheduled"
        
        # Validate datetime fields
        from datetime import datetime, timezone
        assert isinstance(test_flight_data["departure_time"], datetime)
        assert isinstance(test_flight_data["arrival_time"], datetime)
        assert test_flight_data["departure_time"].tzinfo is not None
        assert test_flight_data["arrival_time"].tzinfo is not None
    
    def test_test_flight_create_data_fixture(self, test_flight_create_data):
        """Test that test_flight_create_data fixture has expected structure."""
        required_fields = ["origin", "destination", "departure_time", "arrival_time", "airline", "price", "status"]
        for field in required_fields:
            assert field in test_flight_create_data
            assert test_flight_create_data[field] is not None
        
        # Validate specific values
        assert test_flight_create_data["origin"] == "Boston"
        assert test_flight_create_data["destination"] == "Seattle"
        assert test_flight_create_data["airline"] == "Alaska Airlines"
        assert test_flight_create_data["price"] == 450.0
        assert test_flight_create_data["status"] == "scheduled"
        
        # Validate datetime strings
        assert isinstance(test_flight_create_data["departure_time"], str)
        assert isinstance(test_flight_create_data["arrival_time"], str)
        assert "2025-12-27T09:00:00Z" == test_flight_create_data["departure_time"]
        assert "2025-12-27T12:30:00Z" == test_flight_create_data["arrival_time"]
