"""
Tests for ChatService - Service Layer
Tests focus on business logic, mocking repository layer
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.chat import AgentChatService
from schemas.chat import ChatRequest, ChatMessageResponse, ChatHistoryResponse
from exceptions import AgentInvocationFailedError, ChatMessageSaveFailedError
from repository.chatbot_message import ChatbotMessageRepository

@pytest.mark.asyncio  # Añadir este decorador para tests asíncronos
class TestChatService:
    """Test suite for ChatService."""
    
    @pytest.fixture
    def mock_chat_repo(self):
        """Create a mock chat repository."""
        mock = Mock(spec=ChatbotMessageRepository)
        mock.create.return_value = Mock(
            id=1,
            user_id=1,
            user_message="test message",
            bot_response="test response",
            created_at=datetime.now(timezone.utc)
        )
        return mock

    @pytest.fixture
    def mock_agent(self):
        """Create a mock LangChain agent."""
        from unittest.mock import MagicMock
        mock = AsyncMock()
        message = MagicMock()
        message.content = "mock response"
        mock.ainvoke.return_value = {
            "messages": [message]
        }
        return mock

    @pytest.fixture
    def chat_service(self, mock_chat_repo, mock_agent):
        """Create ChatService instance with mocked dependencies."""
        return AgentChatService(
            agent=mock_agent,
            system_context="test context",
            chat_repo=mock_chat_repo
        )

    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return Mock(
            id=1,
            name="Test User",
            email="test@example.com"
        )

    # ===== POSITIVE TESTS =====

    @pytest.mark.asyncio
    async def test_process_chat_request_success(self, chat_service, sample_user):
        """Test successful chat request processing."""
        # Setup
        request = ChatRequest(content="Hello bot")
        
        # Execute
        response = await chat_service.process_chat_request(sample_user, request)
        
        # Verify response
        assert isinstance(response, str)  # Verify response is a string
        assert response == chat_service.agent.ainvoke.return_value["messages"][0].content  # Verify we return what the agent returned
        
        # Verify agent was called correctly
        chat_service.agent.ainvoke.assert_called_once()
        call_args = chat_service.agent.ainvoke.call_args[0][0]  # Get the first positional argument
        call_kwargs = chat_service.agent.ainvoke.call_args[1]  # Get keyword arguments
        
        # Verify message structure
        assert len(call_args["messages"]) == 2  # System context + user message
        assert call_args["messages"][0]["role"] == "system"
        assert call_args["messages"][0]["content"] == "test context"  # Verify system context
        assert call_args["messages"][1]["role"] == "user"
        assert call_args["messages"][1]["content"] == "Hello bot"  # Verify user message
        
        # Verify session configuration
        assert call_kwargs["config"]["configurable"]["session_id"] == f"chat_session_{sample_user.id}"
        assert call_kwargs["config"]["configurable"]["thread_id"] == f"chat_thread_{sample_user.id}"

    @pytest.mark.asyncio
    async def test_save_chat_message_success(self, chat_service):
        """Test successful chat message saving."""
        await chat_service.save_chat_message(
            user_id=1,
            message="test message",
            response="test response"
        )
        
        chat_service.chat_repo.create.assert_called_once_with(
            user_id=1,
            message="test message",
            response="test response"
        )

    def test_get_chat_history_success(self, chat_service, mock_chat_repo):
        """Test successful chat history retrieval."""
        # Configure mock to return test data
        mock_chat_repo.find_by_user_id.return_value = [
            Mock(
                id=1,
                user_message="message 1",
                bot_response="response 1",
                created_at=datetime.now(timezone.utc)
            ),
            Mock(
                id=2,
                user_message="message 2",
                bot_response="response 2",
                created_at=datetime.now(timezone.utc)
            )
        ]
        mock_chat_repo.count_by_user_id.return_value = 2

        history = chat_service.get_chat_history(user_id=1, limit=10, offset=0)

        assert isinstance(history, ChatHistoryResponse)
        assert len(history.messages) == 2
        assert history.total_count == 2
        mock_chat_repo.find_by_user_id.assert_called_once_with(1, limit=10, offset=0)

    def test_clear_chat_history_success(self, chat_service, mock_chat_repo):
        """Test successful chat history clearing."""
        mock_chat_repo.delete_by_user_id.return_value = 5

        result = chat_service.clear_chat_history(user_id=1)

        assert result["deleted_count"] == 5
        assert "Successfully cleared 5 chat messages" in result["message"]
        mock_chat_repo.delete_by_user_id.assert_called_once_with(1)

    # ===== NEGATIVE TESTS =====

    async def test_process_chat_request_agent_error(self, chat_service, sample_user):
        """Test chat request processing when agent fails."""
        # Setup
        request = ChatRequest(content="Hello bot")
        chat_service.agent.ainvoke.side_effect = Exception("Agent error")

        # Execute & Verify
        with pytest.raises(AgentInvocationFailedError) as exc_info:
            await chat_service.process_chat_request(sample_user, request)

        assert str(exc_info.value.details["user_id"]) == "1"
        assert "Agent error" in str(exc_info.value.details["error_details"])

    async def test_save_chat_message_db_error(self, chat_service, mock_chat_repo):
        """Test chat message saving when database fails."""
        mock_chat_repo.create.side_effect = Exception("DB error")

        with pytest.raises(ChatMessageSaveFailedError) as exc_info:
            await chat_service.save_chat_message(1, "test", "test")

        assert str(exc_info.value.details["user_id"]) == "1"
        assert "DB error" in str(exc_info.value.details["error_details"])

    def test_get_chat_history_empty(self, chat_service, mock_chat_repo):
        """Test chat history retrieval when no messages exist."""
        mock_chat_repo.find_by_user_id.return_value = []
        mock_chat_repo.count_by_user_id.return_value = 0

        history = chat_service.get_chat_history(user_id=1)

        assert len(history.messages) == 0
        assert history.total_count == 0

    # ===== EDGE CASES =====

    def test_get_chat_history_pagination(self, chat_service, mock_chat_repo):
        """Test chat history pagination."""
        # Create 15 mock messages
        mock_messages = [
            Mock(
                id=i,
                user_message=f"message {i}",
                bot_response=f"response {i}",
                created_at=datetime.now(timezone.utc)
            ) for i in range(15)
        ]
        
        mock_chat_repo.count_by_user_id.return_value = 15
        
        # Test first page
        mock_chat_repo.find_by_user_id.return_value = mock_messages[:10]
        page1 = chat_service.get_chat_history(user_id=1, limit=10, offset=0)
        assert len(page1.messages) == 10
        assert page1.total_count == 15
        
        # Test second page
        mock_chat_repo.find_by_user_id.return_value = mock_messages[10:15]
        page2 = chat_service.get_chat_history(user_id=1, limit=10, offset=10)
        assert len(page2.messages) == 5
        assert page2.total_count == 15

    async def test_process_chat_request_long_response(self, chat_service, sample_user):
        """Test processing chat request with long response."""
        # Setup
        long_response = "A" * 1000
        from unittest.mock import MagicMock
        message = MagicMock()
        message.content = long_response
        chat_service.agent.ainvoke.return_value = {
            "messages": [message]
        }
        request = ChatRequest(content="Hello bot")
        
        # Execute
        response = await chat_service.process_chat_request(sample_user, request)
        
        # Verify response
        assert isinstance(response, str)  # Verify response is a string
        assert response == long_response
        assert len(response) == 1000

    def test_clear_chat_history_no_messages(self, chat_service, mock_chat_repo):
        """Test clearing chat history when no messages exist."""
        mock_chat_repo.delete_by_user_id.return_value = 0

        result = chat_service.clear_chat_history(user_id=1)

        assert result["deleted_count"] == 0
        assert "Successfully cleared 0 chat messages" in result["message"]