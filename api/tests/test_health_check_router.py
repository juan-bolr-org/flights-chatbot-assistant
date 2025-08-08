"""
Tests for Health Check Router - Router Layer  
Tests mock the service layer to focus on HTTP concerns using FastAPI dependency overrides.
"""
import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
from datetime import datetime, timezone

# Add src to path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from routers.health_check import router
from services.health import HealthService, create_health_service


class TestHealthCheckRouter:
    """Test suite for Health Check Router with mocked service layer using dependency overrides."""
    
    @pytest.fixture
    def mock_health_service(self):
        """Create mock health service."""
        mock = Mock(spec=HealthService)
        return mock
    
    @pytest.fixture
    def app(self, mock_health_service):
        """Create FastAPI app with mocked dependencies."""
        app = FastAPI()
        app.include_router(router)
        
        # Override dependency
        app.dependency_overrides[create_health_service] = lambda: mock_health_service
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def healthy_status_response(self):
        """Sample healthy status response."""
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resources": {
                "initialized": True,
                "details": {
                    "database": {
                        "status": "healthy",
                        "initialized": True
                    },
                    "crypto": {
                        "status": "healthy", 
                        "initialized": True
                    },
                    "chat": {
                        "status": "healthy",
                        "initialized": True,
                        "model_type": "ChatOpenAI"
                    },
                    "chat_memory": {
                        "status": "healthy",
                        "initialized": True,
                        "memory_type": "MemorySaver"
                    },
                    "logging": {
                        "status": "healthy",
                        "initialized": True
                    },
                    "speech": {
                        "status": "healthy",
                        "configured": True,
                        "environment_variables": {
                            "AZURE_SPEECH_KEY": "set",
                            "AZURE_SPEECH_REGION": "set"
                        },
                        "ffmpeg": {
                            "available": True
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def degraded_status_response(self):
        """Sample degraded status response."""
        return {
            "status": "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resources": {
                "initialized": True,
                "details": {
                    "database": {
                        "status": "unhealthy",
                        "initialized": True,
                        "error": "Connection timeout"
                    },
                    "crypto": {
                        "status": "healthy",
                        "initialized": True
                    },
                    "chat": {
                        "status": "not_initialized",
                        "initialized": False,
                        "model_type": None
                    },
                    "speech": {
                        "status": "not_configured",
                        "configured": False,
                        "environment_variables": {
                            "AZURE_SPEECH_KEY": "not_set",
                            "AZURE_SPEECH_REGION": "not_set"
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def starting_status_response(self):
        """Sample starting status response."""
        return {
            "status": "starting",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resources": {
                "initialized": False,
                "details": {
                    "message": "Application resources not yet initialized"
                }
            }
        }
    
    # ===== HEALTH CHECK ENDPOINT TESTS =====
    
    def test_health_check_healthy_status(self, client, mock_health_service, healthy_status_response):
        """Test health check endpoint when all systems are healthy."""
        # Setup mock
        mock_health_service.get_health_status.return_value = healthy_status_response
        
        # Execute
        response = client.get("/health")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert data["resources"]["initialized"] is True
        assert data["resources"]["details"]["database"]["status"] == "healthy"
        assert data["resources"]["details"]["crypto"]["status"] == "healthy"
        assert data["resources"]["details"]["chat"]["status"] == "healthy"
        assert data["resources"]["details"]["speech"]["status"] == "healthy"
        
        # Verify service was called
        mock_health_service.get_health_status.assert_called_once()
    
    def test_health_check_degraded_status(self, client, mock_health_service, degraded_status_response):
        """Test health check endpoint when some systems are degraded."""
        # Setup mock
        mock_health_service.get_health_status.return_value = degraded_status_response
        
        # Execute
        response = client.get("/health")
        
        # Verify
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "degraded"
        assert data["resources"]["details"]["database"]["status"] == "unhealthy"
        assert "Connection timeout" in data["resources"]["details"]["database"]["error"]
        assert data["resources"]["details"]["chat"]["status"] == "not_initialized"
        
        mock_health_service.get_health_status.assert_called_once()
    
    def test_health_check_starting_status(self, client, mock_health_service, starting_status_response):
        """Test health check endpoint when application is starting."""
        # Setup mock
        mock_health_service.get_health_status.return_value = starting_status_response
        
        # Execute
        response = client.get("/health")
        
        # Verify
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "starting"
        assert data["resources"]["initialized"] is False
        assert "Application resources not yet initialized" in data["resources"]["details"]["message"]
        
        mock_health_service.get_health_status.assert_called_once()
    
    def test_health_check_service_exception(self, client, mock_health_service):
        """Test health check endpoint when service raises an exception."""
        # Setup mock to raise exception
        mock_health_service.get_health_status.side_effect = Exception("Internal service error")
        
        # Execute
        response = client.get("/health")
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        # The response contains "error" field, not "detail"
        assert "error" in data
        assert "status" in data
        assert data["status"] == "error"
    
    def test_health_check_response_structure(self, client, mock_health_service, healthy_status_response):
        """Test that health check response has the expected structure."""
        # Setup mock
        mock_health_service.get_health_status.return_value = healthy_status_response
        
        # Execute
        response = client.get("/health")
        
        # Verify response structure
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Required top-level fields
        assert "status" in data
        assert "timestamp" in data
        assert "resources" in data
        
        # Resources structure
        resources = data["resources"]
        assert "initialized" in resources
        assert "details" in resources
        
        # Details should contain health information for each component
        details = resources["details"]
        expected_components = ["database", "crypto", "chat", "chat_memory", "logging", "speech"]
        for component in expected_components:
            if component in details:
                assert "status" in details[component]
                # Different components have different structure
                if component == "speech":
                    # Speech service uses 'configured' instead of 'initialized'
                    assert "configured" in details[component]
                else:
                    assert "initialized" in details[component]
    
    def test_health_check_endpoint_accessibility(self, client, mock_health_service, healthy_status_response):
        """Test that health check endpoint is accessible without authentication."""
        # Setup mock
        mock_health_service.get_health_status.return_value = healthy_status_response
        
        # Execute without any headers or authentication
        response = client.get("/health")
        
        # Verify that endpoint is accessible
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        # Should not return 401 or 403
        mock_health_service.get_health_status.assert_called_once()
    
    # ===== EDGE CASES =====
    
    def test_health_check_malformed_response(self, client, mock_health_service):
        """Test health check when service returns malformed response."""
        # Setup mock to return malformed response
        mock_health_service.get_health_status.return_value = {"invalid": "response"}
        
        # Execute
        response = client.get("/health")
        
        # Should still work, just return whatever the service provides
        # The status code mapping might default to 500 if status field is missing
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]
    
    def test_health_check_empty_response(self, client, mock_health_service):
        """Test health check when service returns empty response."""
        # Setup mock to return empty response
        mock_health_service.get_health_status.return_value = {}
        
        # Execute
        response = client.get("/health")
        
        # Should handle gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_503_SERVICE_UNAVAILABLE]
        data = response.json()
        # Response should at least be valid JSON
        assert isinstance(data, dict)
    
    def test_health_check_large_response(self, client, mock_health_service):
        """Test health check with large response payload."""
        # Create a large response with many details
        large_response = {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "resources": {
                "initialized": True,
                "details": {
                    f"component_{i}": {
                        "status": "healthy",
                        "initialized": True,
                        "large_data": "x" * 1000  # 1KB of data per component
                    } for i in range(50)  # 50 components
                }
            }
        }
        
        # Setup mock
        mock_health_service.get_health_status.return_value = large_response
        
        # Execute
        response = client.get("/health")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert len(data["resources"]["details"]) == 50
    
    def test_health_check_various_status_codes(self, client, mock_health_service):
        """Test health check endpoint returns appropriate status codes for different health states."""
        test_cases = [
            ("ok", status.HTTP_200_OK),
            ("degraded", status.HTTP_503_SERVICE_UNAVAILABLE),
            ("starting", status.HTTP_503_SERVICE_UNAVAILABLE),
            ("unknown_status", status.HTTP_503_SERVICE_UNAVAILABLE)  # Unknown statuses default to 503
        ]
        
        for health_status, expected_code in test_cases:
            # Setup mock
            mock_health_service.get_health_status.return_value = {
                "status": health_status,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "resources": {"initialized": True, "details": {}}
            }
            
            # Execute
            response = client.get("/health")
            
            # Verify status code matches expected
            assert response.status_code == expected_code, f"Expected {expected_code} for status '{health_status}', got {response.status_code}"
