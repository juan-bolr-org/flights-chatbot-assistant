"""
Test configuration and fixtures for the flights chatbot API tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from unittest.mock import Mock

# Import the models and app
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Base
from resources.crypto import CryptoManager, CryptoConfig


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def crypto_manager():
    """Create a crypto manager for testing."""
    config = CryptoConfig(
        secret_key="test_secret_key_for_testing_only",
        algorithm="HS256",
        access_token_expire_minutes=60
    )
    crypto = CryptoManager(config)
    crypto.initialize()
    return crypto


@pytest.fixture
def mock_crypto_manager():
    """Create a mock crypto manager for service/router testing."""
    mock = Mock(spec=CryptoManager)
    mock.get_password_hash.return_value = "hashed_password"
    mock.verify_password.return_value = True
    mock.create_access_token.return_value = "test_access_token"
    mock.is_initialized.return_value = True
    return mock


@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    # Import here to avoid circular imports
    from main import app
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "secure_password123",
        "phone": "+1234567890"
    }


@pytest.fixture
def test_login_data():
    """Sample login data for testing."""
    return {
        "email": "john.doe@example.com",
        "password": "secure_password123"
    }


@pytest.fixture
def test_flight_data():
    """Sample flight data for testing."""
    from datetime import datetime, timezone
    return {
        "origin": "New York",
        "destination": "Los Angeles",
        "departure_time": datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc),
        "arrival_time": datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc),
        "airline": "American Airlines",
        "price": 299,
        "status": "scheduled"
    }


@pytest.fixture
def test_flight_create_data():
    """Sample flight creation data for testing."""
    return {
        "origin": "Boston",
        "destination": "Seattle",
        "departure_time": "2025-12-27T09:00:00Z",
        "arrival_time": "2025-12-27T12:30:00Z",
        "airline": "Alaska Airlines",
        "price": 450.0,
        "status": "scheduled"
    }
