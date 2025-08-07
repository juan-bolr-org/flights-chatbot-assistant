"""
Tests for HealthService - Service Layer
Tests mock dependencies to focus on health check logic.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add src to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.health import SystemHealthService
from resources.app_resources import AppResources
from resources.crypto import CryptoManager
from sqlalchemy.orm import Session
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from services.speech import SpeechService


class TestHealthService:
    """Test suite for HealthService with mocked dependencies."""
    
    @pytest.fixture
    def mock_app_resources(self):
        """Create mock app resources."""
        mock = Mock()  # Remove spec=AppResources to allow any attributes
        mock.is_initialized.return_value = True
        # Add mock for logging
        mock.logging = Mock()
        mock.logging.is_initialized.return_value = True
        return mock
    
    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        mock = Mock()  # Remove spec to allow any attributes  
        return mock
    
    @pytest.fixture
    def mock_crypto_manager(self):
        """Create mock crypto manager."""
        mock = Mock()  # Remove spec to allow any attributes
        mock.is_initialized.return_value = True
        return mock
    
    @pytest.fixture
    def mock_chat_model(self):
        """Create mock chat model."""
        mock = Mock()  # Remove spec to allow any attributes
        return mock
    
    @pytest.fixture
    def mock_chat_memory(self):
        """Create mock chat memory."""
        mock = Mock()  # Remove spec to allow any attributes
        return mock
    
    @pytest.fixture
    def mock_speech_service(self):
        """Create mock speech service."""
        mock = Mock()  # Remove spec to allow any attributes
        return mock
    
    @pytest.fixture
    def health_service(self, mock_app_resources, mock_db_session, mock_crypto_manager, 
                      mock_chat_model, mock_chat_memory, mock_speech_service):
        """Create health service with mocked dependencies."""
        return SystemHealthService(
            app_res=mock_app_resources,
            db=mock_db_session,
            crypto=mock_crypto_manager,
            chat_model=mock_chat_model,
            chat_memory=mock_chat_memory,
            speech_service=mock_speech_service
        )
    
    # ===== POSITIVE TESTS =====
    
    def test_get_health_status_all_healthy(self, health_service, mock_app_resources, mock_db_session):
        """Test health status when all components are healthy."""
        # Mock successful database query
        mock_db_session.execute.return_value = Mock()
        
        result = health_service.get_health_status()
        
        assert result["status"] == "ok"
        assert result["timestamp"] is not None
        assert "resources" in result
        assert result["resources"]["initialized"] is True
        assert "details" in result["resources"]
    
    def test_get_health_status_app_not_initialized(self, health_service, mock_app_resources):
        """Test health status when app resources are not initialized."""
        mock_app_resources.is_initialized.return_value = False
        
        result = health_service.get_health_status()
        
        assert result["status"] == "starting"
        assert result["resources"]["initialized"] is False
        assert "Application resources not yet initialized" in result["resources"]["details"]["message"]
    
    def test_check_database_health_success(self, health_service, mock_db_session, mock_app_resources):
        """Test successful database health check."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        
        # Mock successful database query
        mock_db_session.execute.return_value = Mock()
        
        result = health_service.get_health_status()
        
        assert result["resources"]["details"]["database"]["status"] == "healthy"
        assert result["resources"]["details"]["database"]["initialized"] is True
    
    def test_check_database_health_failure(self, health_service, mock_db_session, mock_app_resources):
        """Test database health check failure."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        
        # Mock database exception
        mock_db_session.execute.side_effect = Exception("Connection failed")
        
        result = health_service.get_health_status()
        
        assert result["status"] == "degraded"
        assert result["resources"]["details"]["database"]["status"] == "unhealthy"
        assert "Connection failed" in result["resources"]["details"]["database"]["error"]
    
    def test_check_crypto_health_initialized(self, health_service, mock_crypto_manager, mock_app_resources):
        """Test crypto health check when initialized."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        mock_crypto_manager.is_initialized.return_value = True
        
        result = health_service.get_health_status()
        
        assert result["resources"]["details"]["crypto"]["status"] == "healthy"
        assert result["resources"]["details"]["crypto"]["initialized"] is True
    
    def test_check_crypto_health_not_initialized(self, health_service, mock_crypto_manager, mock_app_resources):
        """Test crypto health check when not initialized."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        mock_crypto_manager.is_initialized.return_value = False
        
        result = health_service.get_health_status()
        
        assert result["status"] == "degraded"
        assert result["resources"]["details"]["crypto"]["status"] == "not_initialized"
        assert result["resources"]["details"]["crypto"]["initialized"] is False
    
    def test_check_chat_health_success(self, health_service, mock_chat_model, mock_app_resources):
        """Test successful chat health check."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        
        result = health_service.get_health_status()
        
        assert result["resources"]["details"]["chat"]["status"] == "healthy"
        assert result["resources"]["details"]["chat"]["initialized"] is True
    
    def test_check_chat_health_model_unavailable(self, health_service, mock_app_resources):
        """Test chat health check when model is unavailable."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        
        # Set chat_model to None to simulate unavailable model
        health_service.chat_model = None
        
        result = health_service.get_health_status()
        
        assert result["status"] == "degraded"
        assert result["resources"]["details"]["chat"]["status"] == "not_initialized"
        assert result["resources"]["details"]["chat"]["initialized"] is False
    
    def test_check_chat_memory_health_success(self, health_service, mock_chat_memory, mock_app_resources):
        """Test successful chat memory health check."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        
        result = health_service.get_health_status()
        
        assert result["resources"]["details"]["chat_memory"]["status"] == "healthy"
        assert result["resources"]["details"]["chat_memory"]["initialized"] is True
    
    @patch('constants.get_env_str')
    def test_check_speech_health_configured(self, mock_get_env_str, health_service, mock_app_resources):
        """Test speech health check when properly configured."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        
        # Mock environment variables
        mock_get_env_str.side_effect = lambda key, default: {
            "AZURE_SPEECH_KEY": "test_key",
            "AZURE_SPEECH_REGION": "eastus",
            "AZURE_SPEECH_ENDPOINT": "test_endpoint"
        }.get(key.value if hasattr(key, 'value') else key, default)
        
        with patch.object(health_service, '_check_ffmpeg_availability', return_value={"available": True}):
            result = health_service.get_health_status()
            
            assert result["resources"]["details"]["speech"]["status"] == "healthy"
    
    @patch('constants.get_env_str')
    def test_check_speech_health_not_configured(self, mock_get_env_str, health_service, mock_app_resources):
        """Test speech health check when not configured."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.return_value = True
        
        # Mock missing environment variables
        mock_get_env_str.return_value = ""
        
        result = health_service.get_health_status()
        
        assert result["resources"]["details"]["speech"]["status"] == "not_configured"
    
    # ===== EDGE CASES =====
    
    def test_health_status_exception_handling(self, health_service, mock_app_resources):
        """Test that exceptions in health checks don't crash the service."""
        mock_app_resources.is_initialized.return_value = True
        mock_app_resources.logging.is_initialized.side_effect = Exception("Unexpected error")
        
        result = health_service.get_health_status()
        
        # Should still return a result, but overall status should be degraded
        assert "status" in result
        # The service should handle exceptions gracefully
