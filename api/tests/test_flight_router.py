"""
Tests for Flight Router - Router Layer
Tests mock the service layer to focus on HTTP concerns using FastAPI dependency overrides.
"""
import pytest
import os
import sys
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
from datetime import datetime, timezone

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from routers.flights import router
from services.flight import FlightService, create_flight_service
from schemas.flight import FlightResponse, FlightCreate, PaginatedResponse
from models import User, Flight
from exceptions import InvalidDateFormatError
from resources.dependencies import get_current_user


class TestFlightRouter:
    """Test suite for Flight Router with mocked service layer using dependency overrides."""
    
    @pytest.fixture
    def mock_flight_service(self):
        """Create mock FlightService."""
        return Mock(spec=FlightService)
    
    @pytest.fixture
    def mock_current_user(self):
        """Create mock current user."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "john.doe@example.com"
        user.name = "John Doe"
        return user
    
    @pytest.fixture
    def app(self, mock_flight_service, mock_current_user):
        """Create FastAPI app with dependency overrides."""
        app = FastAPI()
        app.include_router(router)
        
        # Override dependencies
        app.dependency_overrides[create_flight_service] = lambda: mock_flight_service
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_flight_response(self):
        """Create sample FlightResponse for testing."""
        return FlightResponse(
            id=1,
            origin="New York",
            destination="Los Angeles",
            departure_time=datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc),
            airline="American Airlines",
            status="scheduled",
            price=299  # Changed from float to int
        )
    
    @pytest.fixture
    def sample_flight_list(self):
        """Create sample list of flight responses for testing."""
        flight1 = FlightResponse(
            id=1,
            origin="New York",
            destination="Los Angeles",
            departure_time=datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc),
            airline="American Airlines",
            status="scheduled",
            price=299  # Changed from float to int
        )
        
        flight2 = FlightResponse(
            id=2,
            origin="Chicago",
            destination="Miami",
            departure_time=datetime(2025, 12, 26, 14, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 26, 17, 45, 0, tzinfo=timezone.utc),
            airline="Delta Airlines",
            status="scheduled",
            price=399  # Changed from float to int
        )
        
        return [flight1, flight2]
    
    @pytest.fixture
    def sample_flight_create_data(self):
        """Create sample flight creation data for testing."""
        return {
            "origin": "Boston",
            "destination": "Seattle",
            "departure_time": "2025-12-27T09:00:00Z",
            "arrival_time": "2025-12-27T12:30:00Z",
            "airline": "Alaska Airlines",
            "price": 450.0,
            "status": "scheduled"
        }
    
    # ===== SEARCH FLIGHTS ENDPOINT TESTS =====
    
    def test_search_flights_success(self, client, mock_flight_service, sample_flight_list):
        """Test successful flight search."""
        # Setup mock to return PaginatedResponse
        paginated_response = PaginatedResponse(
            items=sample_flight_list,
            total=2,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.search_flights.return_value = paginated_response
        
        # Execute
        response = client.get("/flights/search?origin=New York&destination=Los Angeles&departure_date=2025-12-25")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 1
        assert len(data["items"]) == 2
        assert data["items"][0]["id"] == 1
        assert data["items"][0]["origin"] == "New York"
        assert data["items"][0]["destination"] == "Los Angeles"
        assert data["items"][1]["id"] == 2
        assert data["items"][1]["origin"] == "Chicago"
        
        # Verify service was called with new signature
        mock_flight_service.search_flights.assert_called_once_with("New York", "Los Angeles", "2025-12-25", 1, 10)
    
    def test_search_flights_empty_result(self, client, mock_flight_service):
        """Test flight search with no results."""
        # Setup mock to return empty PaginatedResponse
        paginated_response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.search_flights.return_value = paginated_response
        
        # Execute
        response = client.get("/flights/search?origin=Boston&destination=Seattle&departure_date=2025-12-25")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
        
        # Verify service was called with new signature
        mock_flight_service.search_flights.assert_called_once_with("Boston", "Seattle", "2025-12-25", 1, 10)
    
    def test_search_flights_invalid_date_format(self, client, mock_flight_service):
        """Test flight search with invalid date format."""
        # Setup mock
        mock_flight_service.search_flights.side_effect = InvalidDateFormatError("2025/12/25")
        
        # Execute
        response = client.get("/flights/search?origin=New York&destination=Los Angeles&departure_date=2025/12/25")
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "INVALID_DATE_FORMAT"
        assert "Invalid date format" in data["detail"]["message"]
        assert data["detail"]["details"]["provided_date"] == "2025/12/25"
    
    def test_search_flights_internal_error(self, client, mock_flight_service):
        """Test flight search with unexpected internal error."""
        # Setup mock
        mock_flight_service.search_flights.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.get("/flights/search?origin=New York&destination=Los Angeles&departure_date=2025-12-25")
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error searching flights" in data["detail"]
    
    def test_search_flights_missing_parameters(self, client, mock_flight_service):
        """Test flight search with no parameters (should now work with all optional)."""
        # Setup mock to return empty PaginatedResponse
        paginated_response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.search_flights.return_value = paginated_response
        
        # No parameters should work now
        response = client.get("/flights/search")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
        
        # Verify service was called with None values
        mock_flight_service.search_flights.assert_called_once_with(None, None, None, 1, 10)
    
    def test_search_flights_special_characters(self, client, mock_flight_service, sample_flight_list):
        """Test flight search with special characters in city names."""
        # Setup mock to return PaginatedResponse
        paginated_response = PaginatedResponse(
            items=sample_flight_list,
            total=2,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.search_flights.return_value = paginated_response

        # Execute with URL-encoded special characters
        response = client.get("/flights/search?origin=São Paulo&destination=México City&departure_date=2025-12-25")

        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert response.status_code == status.HTTP_200_OK

        # Verify service was called with decoded characters and pagination parameters
        mock_flight_service.search_flights.assert_called_once_with("São Paulo", "México City", "2025-12-25", 1, 10)    # ===== CREATE FLIGHT ENDPOINT TESTS =====
    
    def test_create_flight_success(self, client, mock_flight_service, sample_flight_create_data, sample_flight_response):
        """Test successful flight creation."""
        # Setup mock
        mock_flight_service.create_flight.return_value = sample_flight_response
        
        # Execute
        response = client.post("/flights", json=sample_flight_create_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["origin"] == "New York"
        assert data["destination"] == "Los Angeles"
        assert data["airline"] == "American Airlines"
        assert data["price"] == 299  # Changed from float to int
        assert data["status"] == "scheduled"
        
        # Verify service was called
        mock_flight_service.create_flight.assert_called_once()
    
    def test_create_flight_without_status(self, client, mock_flight_service, sample_flight_response):
        """Test flight creation without status field."""
        flight_data = {
            "origin": "Boston",
            "destination": "Seattle",
            "departure_time": "2025-12-27T09:00:00Z",
            "arrival_time": "2025-12-27T12:30:00Z",
            "airline": "Alaska Airlines",
            "price": 450.0
        }
        
        # Setup mock
        mock_flight_service.create_flight.return_value = sample_flight_response
        
        # Execute
        response = client.post("/flights", json=flight_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        # Verify service was called
        mock_flight_service.create_flight.assert_called_once()
    
    def test_create_flight_internal_error(self, client, mock_flight_service, sample_flight_create_data):
        """Test flight creation with unexpected internal error."""
        # Setup mock
        mock_flight_service.create_flight.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.post("/flights", json=sample_flight_create_data)
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error creating flight" in data["detail"]
    
    def test_create_flight_missing_required_fields(self, client):
        """Test flight creation with missing required fields."""
        # Missing origin
        invalid_data = {
            "destination": "Seattle",
            "departure_time": "2025-12-27T09:00:00Z",
            "arrival_time": "2025-12-27T12:30:00Z",
            "airline": "Alaska Airlines",
            "price": 450.0
        }
        
        response = client.post("/flights", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # ===== LIST FLIGHTS ENDPOINT TESTS =====
    
    def test_list_flights_success(self, client, mock_flight_service, sample_flight_list):
        """Test successful flight listing."""
        # Setup mock to return PaginatedResponse
        paginated_response = PaginatedResponse(
            items=sample_flight_list,
            total=2,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.list_flights.return_value = paginated_response
        
        # Execute
        response = client.get("/flights/list")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2
        assert data["items"][0]["id"] == 1
        assert data["items"][0]["origin"] == "New York"
        assert data["items"][1]["id"] == 2
        assert data["items"][1]["origin"] == "Chicago"
        
        # Verify service was called with pagination defaults
        mock_flight_service.list_flights.assert_called_once_with(1, 10)
    
    def test_list_flights_empty(self, client, mock_flight_service):
        """Test flight listing when no flights exist."""
        # Setup mock to return empty PaginatedResponse
        paginated_response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.list_flights.return_value = paginated_response
        
        # Execute
        response = client.get("/flights/list")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0
        
        # Verify service was called with pagination defaults
        mock_flight_service.list_flights.assert_called_once_with(1, 10)
    
    def test_list_flights_internal_error(self, client, mock_flight_service):
        """Test flight listing with unexpected internal error."""
        # Setup mock
        mock_flight_service.list_flights.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.get("/flights/list")
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error retrieving flights" in data["detail"]
    
    # ===== AUTHENTICATION TESTS =====
    
    def test_create_flight_without_authentication(self):
        """Test flight creation without authentication (dependency override removed)."""
        # Create app without authentication override
        app = FastAPI()
        app.include_router(router)
        
        # Only override flight service, not authentication
        mock_flight_service = Mock(spec=FlightService)
        app.dependency_overrides[create_flight_service] = lambda: mock_flight_service
        
        client = TestClient(app)
        
        flight_data = {
            "origin": "Boston",
            "destination": "Seattle",
            "departure_time": "2025-12-27T09:00:00Z",
            "arrival_time": "2025-12-27T12:30:00Z",
            "airline": "Alaska Airlines",
            "price": 450.0
        }
        
        # This should fail because get_current_user dependency is not satisfied
        response = client.post("/flights", json=flight_data)
        # The exact status code depends on how get_current_user is implemented
        # but it should not be 200
        assert response.status_code != status.HTTP_200_OK
    
    # ===== EDGE CASES =====
    
    def test_search_flights_very_long_city_names(self, client, mock_flight_service, sample_flight_list):
        """Test flight search with very long city names."""
        # Setup mock to return PaginatedResponse
        paginated_response = PaginatedResponse(
            items=sample_flight_list,
            total=2,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.search_flights.return_value = paginated_response
        
        long_origin = "A" * 100
        long_destination = "B" * 100
        
        # Execute
        response = client.get(f"/flights/search?origin={long_origin}&destination={long_destination}&departure_date=2025-12-25")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        # Verify service was called with long names and pagination defaults
        mock_flight_service.search_flights.assert_called_once_with(long_origin, long_destination, "2025-12-25", 1, 10)
    
    def test_create_flight_extreme_price(self, client, mock_flight_service, sample_flight_response):
        """Test flight creation with extreme price."""
        extreme_price_data = {
            "origin": "Luxury City",
            "destination": "Premium Town",
            "departure_time": "2025-12-27T09:00:00Z",
            "arrival_time": "2025-12-27T12:30:00Z",
            "airline": "Premium Airlines",
            "price": 999999.99  # Very high price
        }
        
        # Setup mock
        mock_flight_service.create_flight.return_value = sample_flight_response
        
        # Execute
        response = client.post("/flights", json=extreme_price_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        # Verify service was called
        mock_flight_service.create_flight.assert_called_once()
    
    def test_search_flights_future_date(self, client, mock_flight_service, sample_flight_list):
        """Test flight search with far future date."""
        # Setup mock to return PaginatedResponse
        paginated_response = PaginatedResponse(
            items=sample_flight_list,
            total=2,
            page=1,
            size=10,
            pages=1
        )
        mock_flight_service.search_flights.return_value = paginated_response
        
        # Execute with far future date
        response = client.get("/flights/search?origin=Mars&destination=Earth&departure_date=2099-12-31")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        # Verify service was called with pagination defaults
        mock_flight_service.search_flights.assert_called_once_with("Mars", "Earth", "2099-12-31", 1, 10)
