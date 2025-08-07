"""
Integration tests for the chat system with SQLite checkpointing.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports_work():
    """Test that all our new imports work correctly."""
    # Test chat service imports
    from services.chat import ChatService, AgentChatService, create_chat_service
    from schemas.chat import ChatRequest, ChatResponse, ChatSessionsResponse, DeleteSessionResponse
    from resources.chat import ChatManager, ChatConfig, chat_manager
    
    # Test that SqliteSaver can be imported
    from langgraph.checkpoint.sqlite import SqliteSaver
    
    assert ChatService is not None
    assert AgentChatService is not None
    assert ChatRequest is not None
    assert ChatResponse is not None
    assert ChatSessionsResponse is not None
    assert DeleteSessionResponse is not None
    assert ChatManager is not None
    assert ChatConfig is not None
    assert SqliteSaver is not None
    assert chat_manager is not None

def test_chat_config_creation():
    """Test ChatConfig creation with defaults."""
    from resources.chat import ChatConfig
    
    config = ChatConfig()
    assert config.model_name == "openai:gpt-4.1"
    assert config.temperature == 0.0
    assert "sqlite:///" in config.checkpoint_db_path
    assert "flight booking assistant" in config.system_context

def test_chat_manager_initialization():
    """Test ChatManager initialization."""
    from resources.chat import ChatManager, ChatConfig
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        temp_db_path = f"sqlite:///{temp_db.name}"
        
        try:
            config = ChatConfig(checkpoint_db_path=temp_db_path)
            manager = ChatManager(config)
            
            # Test that it can initialize
            assert manager is not None
            assert not manager._is_initialized
            
        finally:
            # Clean up
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)

def test_session_id_generation():
    """Test session ID generation."""
    from resources.chat import ChatManager
    
    manager = ChatManager()
    
    # Test with custom session name
    session_id = manager.generate_session_id(123, "test_session")
    assert session_id == "user_123_session_test_session"
    
    # Test with auto-generated session ID
    session_id = manager.generate_session_id(123)
    assert session_id.startswith("user_123_session_")
    assert len(session_id) > len("user_123_session_")

def test_schema_validations():
    """Test that our new schemas work correctly."""
    from schemas.chat import ChatRequest, ChatResponse, ChatSessionsResponse, DeleteSessionResponse
    
    # Test ChatRequest with session_id
    request = ChatRequest(content="Hello", session_id="test_session")
    assert request.content == "Hello"
    assert request.session_id == "test_session"
    
    # Test ChatRequest without session_id
    request = ChatRequest(content="Hello")
    assert request.content == "Hello"
    assert request.session_id is None
    
    # Test ChatResponse
    response = ChatResponse(response="Hi there", session_id="test_session", session_alias="Test Session")
    assert response.response == "Hi there"
    assert response.session_id == "test_session"
    assert response.session_alias == "Test Session"
    
    # Test ChatSessionsResponse
    from schemas.chat import ChatSessionInfo
    from datetime import datetime
    
    session_info = ChatSessionInfo(
        session_id="session1",
        alias="Session 1",
        message_count=5,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    sessions_response = ChatSessionsResponse(sessions=[session_info], total_count=1)
    assert len(sessions_response.sessions) == 1
    assert sessions_response.total_count == 1
    assert sessions_response.sessions[0].session_id == "session1"
    assert sessions_response.sessions[0].alias == "Session 1"
    
    # Test DeleteSessionResponse
    delete_response = DeleteSessionResponse(
        message="Deleted successfully",
        session_id="test_session",
        deleted_count=5
    )
    assert delete_response.message == "Deleted successfully"
    assert delete_response.session_id == "test_session"
    assert delete_response.deleted_count == 5

@patch('resources.chat.create_faqs_retriever_tool')
@patch('resources.chat.init_chat_model')
def test_chat_manager_mock_initialization(mock_init_chat_model, mock_create_faqs_tool):
    """Test ChatManager initialization with mocked dependencies."""
    from resources.chat import ChatManager, ChatConfig
    
    # Mock the dependencies
    mock_init_chat_model.return_value = Mock()
    mock_create_faqs_tool.return_value = Mock()
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        temp_db_path = f"sqlite:///{temp_db.name}"
        
        try:
            config = ChatConfig(checkpoint_db_path=temp_db_path)
            manager = ChatManager(config)
            
            # Test initialization
            manager.initialize()
            
            assert manager._is_initialized
            assert mock_init_chat_model.called
            assert mock_create_faqs_tool.called
            
        finally:
            # Clean up
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)

def test_sqlite_saver_connection():
    """Test that SqliteSaver can connect to a database."""
    from langgraph.checkpoint.sqlite import SqliteSaver
    
    # Create a temporary database for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        temp_db_path = f"sqlite:///{temp_db.name}"
        
        try:
            # Test SqliteSaver creation
            saver = SqliteSaver.from_conn_string(temp_db_path)
            assert saver is not None
            
        finally:
            # Clean up
            if os.path.exists(temp_db.name):
                os.unlink(temp_db.name)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
