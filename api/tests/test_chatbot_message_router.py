"""
Tests for Chat Router - Router Layer
Tests mock the service layer to focus on HTTP concerns using FastAPI dependency overrides.
"""

import pytest
import sys
import os
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from routers.chat import router
from services.chat import ChatService, create_chat_service
from schemas.chat import ChatResponse, ChatHistoryResponse, ChatMessageResponse
from exceptions import AgentInvocationFailedError, ChatMessageSaveFailedError
from resources.dependencies import get_current_user
from datetime import datetime, timezone


class TestChatRouter:
    """Test suite for Chat Router with mocked service layer using dependency overrides."""
    
    @pytest.fixture
    def mock_chat_service(self):
        """Create a mock chat service."""
        mock = Mock(spec=ChatService)
        # Configure default successful responses
        mock.process_chat_request.return_value = "Test response"
        mock.get_chat_history.return_value = ChatHistoryResponse(
            messages=[
                ChatMessageResponse(
                    id=1,
                    message="test message",
                    response="test response",
                    created_at=datetime.now(timezone.utc)
                )
            ],
            total_count=1
        )
        mock.clear_chat_history.return_value = {
            "message": "Successfully cleared 1 chat messages",
            "deleted_count": 1
        }
        return mock

    @pytest.fixture
    def mock_current_user(self):
        """Create a mock authenticated user."""
        return Mock(
            id=1,
            email="test@example.com",
            name="Test User"
        )

    @pytest.fixture
    def app(self, mock_chat_service, mock_current_user):
        """Create FastAPI test application with dependency overrides."""
        app = FastAPI()
        app.include_router(router)
        
        # Override dependencies with direct references to dependencies
        app.dependency_overrides = {
            create_chat_service: lambda: mock_chat_service,
            get_current_user: lambda: mock_current_user
        }
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_chat_request(self):
        """Sample chat request data."""
        return {
            "content": "Hello bot"
        }

    # ===== CHAT ENDPOINT TESTS =====

    def test_chat_success(self, client, mock_chat_service, sample_chat_request):
        """Test successful chat request."""
        # Setup
        expected_response = "Test response"
        mock_chat_service.process_chat_request.return_value = expected_response

        # Execute
        response = client.post("/chat", json=sample_chat_request)

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["response"] == expected_response
        assert mock_chat_service.process_chat_request.called
        assert mock_chat_service.save_chat_message.called

    def test_chat_agent_error(self, client, mock_chat_service, sample_chat_request):
        """Test chat request when agent fails."""
        # Setup
        mock_chat_service.process_chat_request.side_effect = AgentInvocationFailedError(1, "Agent error")

        # Execute
        response = client.post("/chat", json=sample_chat_request)

        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert data["detail"]["error_code"] == "AGENT_INVOCATION_FAILED"
        assert data["detail"]["details"]["user_id"] == 1
        assert "Agent error" in str(data["detail"]["details"]["error_details"])

    def test_chat_save_error(self, client, mock_chat_service, sample_chat_request):
        """Test chat request when saving message fails."""
        # Setup
        mock_chat_service.save_chat_message.side_effect = ChatMessageSaveFailedError(1, "DB error")

        # Execute
        response = client.post("/chat", json=sample_chat_request)

        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "CHAT_MESSAGE_SAVE_FAILED"
        assert data["detail"]["details"]["user_id"] == 1
        assert "DB error" in str(data["detail"]["details"]["error_details"])

    def test_chat_missing_content(self, client):
        """Test chat request with missing content."""
        response = client.post("/chat", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "content" in data["detail"][0]["loc"]  # Verify the error is about missing content field
        assert data["detail"][0]["type"] == "missing"  # Verify it's a missing field error

    def test_chat_null_content(self, client):
        """Test chat request with null content."""
        response = client.post("/chat", json={"content": None})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "content" in data["detail"][0]["loc"]

    # ===== CHAT HISTORY ENDPOINT TESTS =====

    def test_get_chat_history_success(self, client, mock_chat_service):
        """Test successful chat history retrieval."""
        # Setup
        mock_messages = [
            ChatMessageResponse(
                id=1,
                message="test message",
                response="test response",
                created_at=datetime.now(timezone.utc)
            )
        ]
        mock_chat_service.get_chat_history.return_value = ChatHistoryResponse(
            messages=mock_messages,
            total_count=1
        )

        # Execute
        response = client.get("/chat/history")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["messages"]) == 1
        assert data["messages"][0]["message"] == "test message"
        mock_chat_service.get_chat_history.assert_called_once_with(1, limit=50, offset=0)

    def test_get_chat_history_with_pagination(self, client, mock_chat_service):
        """Test chat history retrieval with pagination parameters."""
        # Execute
        response = client.get("/chat/history?limit=10&offset=20")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        mock_chat_service.get_chat_history.assert_called_once_with(1, limit=10, offset=20)

    def test_get_chat_history_with_invalid_limit(self, client, mock_chat_service):
        """Test chat history retrieval with invalid limit parameter."""
        response = client.get("/chat/history?limit=-1")
        assert response.status_code == status.HTTP_200_OK  # FastAPI converts to default value
        data = response.json()
        assert len(data["messages"]) <= 50  # Default limit should be applied

    def test_get_chat_history_with_non_numeric_params(self, client):
        """Test chat history retrieval with non-numeric parameters."""
        response = client.get("/chat/history?limit=abc&offset=def")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert any("limit" in error["loc"] for error in data["detail"])  # Verify limit validation error
        assert any("offset" in error["loc"] for error in data["detail"])  # Verify offset validation error

    # ===== CLEAR CHAT HISTORY ENDPOINT TESTS =====

    def test_clear_chat_history_success(self, client, mock_chat_service):
        """Test successful chat history clearing."""
        # Setup
        mock_chat_service.clear_chat_history.return_value = {
            "message": "Successfully cleared 5 chat messages",
            "deleted_count": 5
        }

        # Execute
        response = client.delete("/chat/history")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted_count"] == 5
        assert "Successfully cleared 5 chat messages" in data["message"]
        mock_chat_service.clear_chat_history.assert_called_once_with(1)

    def test_clear_chat_history_no_messages(self, client, mock_chat_service):
        """Test clearing chat history when no messages exist."""
        # Setup
        mock_chat_service.clear_chat_history.return_value = {
            "message": "Successfully cleared 0 chat messages",
            "deleted_count": 0
        }

        # Execute
        response = client.delete("/chat/history")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted_count"] == 0
        assert "Successfully cleared 0 chat messages" in data["message"]

    def test_clear_chat_history_error(self, client, mock_chat_service):
        """Test clearing chat history when an error occurs."""
        # Setup
        mock_chat_service.clear_chat_history.side_effect = Exception("Database error")

        # Execute
        response = client.delete("/chat/history")

        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error clearing chat history" in data["detail"]
