"""
Tests for Booking Router - Router Layer
Tests mock the service layer to focus on HTTP concerns using FastAPI dependency overrides.
"""
import pytest
import sys
import os
from unittest.mock import Mock
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
from datetime import datetime, timezone

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from routers.bookings import router
from services.booking import BookingService, create_booking_service
from schemas.booking import BookingResponse, BookingCreate, BookingUpdate
from schemas.flight import FlightResponse, PaginatedResponse
from models import User, Booking, Flight
from exceptions import (
    ApiException, 
    ErrorCode, 
    FlightNotAvailableError, 
    BookingAlreadyExistsError, 
    BookingNotFoundError,
    AccessDeniedError,
    BookingCannotBeCancelledError,
    PastFlightCannotBeCancelledError
)
from resources.dependencies import get_current_user


class TestBookingRouter:
    """Test suite for Booking Router with mocked service layer using dependency overrides."""
    
    @pytest.fixture
    def mock_booking_service(self):
        """Create a mock BookingService."""
        return Mock(spec=BookingService)
    
    @pytest.fixture
    def mock_current_user(self):
        """Create a mock current user."""
        return User(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
            phone="+1234567890"
        )
    
    @pytest.fixture
    def app(self, mock_booking_service, mock_current_user):
        """Create FastAPI app with dependency overrides."""
        app = FastAPI()
        app.include_router(router)
        
        # Override dependencies
        app.dependency_overrides[create_booking_service] = lambda: mock_booking_service
        app.dependency_overrides[get_current_user] = lambda: mock_current_user
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_flight_response(self):
        """Create sample flight response data."""
        return FlightResponse(
            id=1,
            origin="New York",
            destination="Los Angeles",
            departure_time=datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc),
            airline="American Airlines",
            price=299,
            status="scheduled"
        )
    
    @pytest.fixture
    def sample_booking_response(self, sample_flight_response):
        """Create sample booking response data."""
        return BookingResponse(
            id=1,
            flight_id=1,
            status="booked",
            booked_at=datetime(2025, 8, 5, 12, 0, 0, tzinfo=timezone.utc),
            cancelled_at=None,
            flight=sample_flight_response
        )
    
    @pytest.fixture
    def sample_cancelled_booking_response(self, sample_flight_response):
        """Create sample cancelled booking response data."""
        return BookingResponse(
            id=2,
            flight_id=1,
            status="cancelled",
            booked_at=datetime(2025, 8, 5, 12, 0, 0, tzinfo=timezone.utc),
            cancelled_at=datetime(2025, 8, 5, 13, 0, 0, tzinfo=timezone.utc),
            flight=sample_flight_response
        )
    
    @pytest.fixture
    def sample_booking_list(self, sample_booking_response, sample_cancelled_booking_response):
        """Create sample list of bookings."""
        return [sample_booking_response, sample_cancelled_booking_response]
    
    @pytest.fixture
    def sample_booking_create_data(self):
        """Create sample booking creation data."""
        return {"flight_id": 1}
    
    @pytest.fixture
    def sample_booking_update_data(self):
        """Create sample booking update data."""
        return {"status": "cancelled"}
    
    # ===== CREATE BOOKING ENDPOINT TESTS =====
    
    def test_create_booking_success(self, client, mock_booking_service, sample_booking_create_data, sample_booking_response):
        """Test successful booking creation."""
        # Setup mock
        mock_booking_service.create_booking.return_value = sample_booking_response
        
        # Execute
        response = client.post("/bookings", json=sample_booking_create_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["flight_id"] == 1
        assert data["status"] == "booked"
        assert data["cancelled_at"] is None
        assert "flight" in data
        
        # Verify service was called
        mock_booking_service.create_booking.assert_called_once()
    
    def test_create_booking_flight_not_available(self, client, mock_booking_service, sample_booking_create_data):
        """Test booking creation when flight is not available."""
        # Setup mock
        mock_booking_service.create_booking.side_effect = FlightNotAvailableError(1)
        
        # Execute
        response = client.post("/bookings", json=sample_booking_create_data)
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["error_code"] == "FLIGHT_NOT_AVAILABLE"
        assert "Flight 1 is not available for booking" in data["detail"]["message"]
        assert data["detail"]["details"]["flight_id"] == 1
    
    def test_create_booking_already_exists(self, client, mock_booking_service, sample_booking_create_data):
        """Test booking creation when booking already exists."""
        # Setup mock
        mock_booking_service.create_booking.side_effect = BookingAlreadyExistsError(1, 1)
        
        # Execute
        response = client.post("/bookings", json=sample_booking_create_data)
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "BOOKING_ALREADY_EXISTS"
        assert "already have a booking" in data["detail"]["message"]
        assert data["detail"]["details"]["user_id"] == 1
        assert data["detail"]["details"]["flight_id"] == 1
    
    def test_create_booking_internal_error(self, client, mock_booking_service, sample_booking_create_data):
        """Test booking creation with internal error."""
        # Setup mock
        mock_booking_service.create_booking.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.post("/bookings", json=sample_booking_create_data)
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error creating booking" in data["detail"]
    
    def test_create_booking_missing_flight_id(self, client):
        """Test booking creation with missing flight_id."""
        invalid_data = {}
        
        response = client.post("/bookings", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_booking_invalid_flight_id_type(self, client):
        """Test booking creation with invalid flight_id type."""
        invalid_data = {"flight_id": "not_a_number"}
        
        response = client.post("/bookings", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # ===== UPDATE BOOKING ENDPOINT TESTS =====
    
    def test_update_booking_success(self, client, mock_booking_service, sample_booking_update_data, sample_cancelled_booking_response):
        """Test successful booking update."""
        # Setup mock
        mock_booking_service.update_booking.return_value = sample_cancelled_booking_response
        
        # Execute
        response = client.patch("/bookings/1", json=sample_booking_update_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 2
        assert data["status"] == "cancelled"
        assert data["cancelled_at"] is not None
        
        # Verify service was called
        mock_booking_service.update_booking.assert_called_once()
    
    def test_update_booking_not_found(self, client, mock_booking_service, sample_booking_update_data):
        """Test updating non-existent booking."""
        # Setup mock
        mock_booking_service.update_booking.side_effect = BookingNotFoundError(999)
        
        # Execute
        response = client.patch("/bookings/999", json=sample_booking_update_data)
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["error_code"] == "BOOKING_NOT_FOUND"
        assert "Booking 999 not found" in data["detail"]["message"]
        assert data["detail"]["details"]["booking_id"] == 999
    
    def test_update_booking_access_denied(self, client, mock_booking_service, sample_booking_update_data):
        """Test updating booking with access denied."""
        # Setup mock
        mock_booking_service.update_booking.side_effect = AccessDeniedError("booking", 1, 2)
        
        # Execute
        response = client.patch("/bookings/1", json=sample_booking_update_data)
        
        # Verify
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert data["detail"]["error_code"] == "ACCESS_DENIED"
        assert "Access denied" in data["detail"]["message"]
    
    def test_update_booking_cannot_be_cancelled(self, client, mock_booking_service, sample_booking_update_data):
        """Test updating booking that cannot be cancelled."""
        # Setup mock
        mock_booking_service.update_booking.side_effect = BookingCannotBeCancelledError(1, "cancelled")
        
        # Execute
        response = client.patch("/bookings/1", json=sample_booking_update_data)
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "BOOKING_CANNOT_BE_CANCELLED"
        assert "Only booked flights can be cancelled" in data["detail"]["message"]
    
    def test_update_booking_past_flight(self, client, mock_booking_service, sample_booking_update_data):
        """Test updating booking for past flight."""
        # Setup mock
        mock_booking_service.update_booking.side_effect = PastFlightCannotBeCancelledError(1, 1)
        
        # Execute
        response = client.patch("/bookings/1", json=sample_booking_update_data)
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "PAST_FLIGHT_CANNOT_BE_CANCELLED"
        assert "Cannot cancel past flights" in data["detail"]["message"]
    
    def test_update_booking_internal_error(self, client, mock_booking_service, sample_booking_update_data):
        """Test booking update with internal error."""
        # Setup mock
        mock_booking_service.update_booking.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.patch("/bookings/1", json=sample_booking_update_data)
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error updating booking" in data["detail"]
    
    def test_update_booking_missing_status(self, client):
        """Test booking update with missing status."""
        invalid_data = {}
        
        response = client.patch("/bookings/1", json=invalid_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_booking_invalid_booking_id(self, client, sample_booking_update_data):
        """Test booking update with invalid booking_id."""
        response = client.patch("/bookings/not_a_number", json=sample_booking_update_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # ===== DELETE BOOKING ENDPOINT TESTS =====
    
    def test_delete_booking_success(self, client, mock_booking_service):
        """Test successful booking deletion."""
        # Setup mock
        mock_booking_service.delete_booking.return_value = {"message": "Booking cancelled successfully"}
        
        # Execute
        response = client.delete("/bookings/1")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Booking cancelled successfully"
        
        # Verify service was called
        mock_booking_service.delete_booking.assert_called_once()
    
    def test_delete_booking_not_found(self, client, mock_booking_service):
        """Test deleting non-existent booking."""
        # Setup mock
        mock_booking_service.delete_booking.side_effect = BookingNotFoundError(999)
        
        # Execute
        response = client.delete("/bookings/999")
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["error_code"] == "BOOKING_NOT_FOUND"
        assert "Booking 999 not found" in data["detail"]["message"]
    
    def test_delete_booking_access_denied(self, client, mock_booking_service):
        """Test deleting booking with access denied."""
        # Setup mock
        mock_booking_service.delete_booking.side_effect = AccessDeniedError("booking", 1, 2)
        
        # Execute
        response = client.delete("/bookings/1")
        
        # Verify
        assert response.status_code == status.HTTP_403_FORBIDDEN
        data = response.json()
        assert data["detail"]["error_code"] == "ACCESS_DENIED"
        assert "Access denied" in data["detail"]["message"]
    
    def test_delete_booking_cannot_be_cancelled(self, client, mock_booking_service):
        """Test deleting booking that cannot be cancelled."""
        # Setup mock
        mock_booking_service.delete_booking.side_effect = BookingCannotBeCancelledError(1, "cancelled")
        
        # Execute
        response = client.delete("/bookings/1")
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "BOOKING_CANNOT_BE_CANCELLED"
        assert "Only booked flights can be cancelled" in data["detail"]["message"]
    
    def test_delete_booking_past_flight(self, client, mock_booking_service):
        """Test deleting booking for past flight."""
        # Setup mock
        mock_booking_service.delete_booking.side_effect = PastFlightCannotBeCancelledError(1, 1)
        
        # Execute
        response = client.delete("/bookings/1")
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["detail"]["error_code"] == "PAST_FLIGHT_CANNOT_BE_CANCELLED"
        assert "Cannot cancel past flights" in data["detail"]["message"]
    
    def test_delete_booking_internal_error(self, client, mock_booking_service):
        """Test booking deletion with internal error."""
        # Setup mock
        mock_booking_service.delete_booking.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.delete("/bookings/1")
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error deleting booking" in data["detail"]
    
    def test_delete_booking_invalid_booking_id(self, client):
        """Test booking deletion with invalid booking_id."""
        response = client.delete("/bookings/not_a_number")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # ===== GET USER BOOKINGS ENDPOINT TESTS =====
    
    def test_get_user_bookings_success(self, client, mock_booking_service, sample_booking_list):
        """Test successful retrieval of user bookings."""
        # Setup mock with PaginatedResponse
        paginated_response = PaginatedResponse(
            items=sample_booking_list,
            total=len(sample_booking_list),
            page=1,
            size=10,
            pages=1
        )
        mock_booking_service.get_user_bookings.return_value = paginated_response
        
        # Execute
        response = client.get("/bookings/user")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 2
        assert data["items"][0]["id"] == 1
        assert data["items"][0]["status"] == "booked"
        assert data["items"][1]["id"] == 2
        assert data["items"][1]["status"] == "cancelled"
        assert data["total"] == 2
        assert data["page"] == 1
        
        # Verify service was called
        mock_booking_service.get_user_bookings.assert_called_once()
    
    def test_get_user_bookings_with_status_filter(self, client, mock_booking_service, sample_booking_list):
        """Test retrieval of user bookings with status filter."""
        # Filter to only booked bookings
        booked_bookings = [b for b in sample_booking_list if b.status == "booked"]
        
        # Setup mock with PaginatedResponse
        paginated_response = PaginatedResponse(
            items=booked_bookings,
            total=len(booked_bookings),
            page=1,
            size=10,
            pages=1
        )
        mock_booking_service.get_user_bookings.return_value = paginated_response
        
        # Execute
        response = client.get("/bookings/user?status=booked")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "booked"
        assert data["total"] == 1
        
        # Verify service was called with filter
        mock_booking_service.get_user_bookings.assert_called_once()
    
    def test_get_user_bookings_empty(self, client, mock_booking_service):
        """Test retrieval of user bookings when user has no bookings."""
        # Setup mock with empty PaginatedResponse
        paginated_response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=0
        )
        mock_booking_service.get_user_bookings.return_value = paginated_response
        
        # Execute
        response = client.get("/bookings/user")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 0
        assert data["total"] == 0
        
        # Verify service was called
        mock_booking_service.get_user_bookings.assert_called_once()
    
    def test_get_user_bookings_upcoming_filter(self, client, mock_booking_service, sample_booking_list):
        """Test retrieval of upcoming bookings."""
        # Filter to only upcoming bookings
        upcoming_bookings = [b for b in sample_booking_list if b.status == "booked"]
        
        # Setup mock with PaginatedResponse
        paginated_response = PaginatedResponse(
            items=upcoming_bookings,
            total=len(upcoming_bookings),
            page=1,
            size=10,
            pages=1
        )
        mock_booking_service.get_user_bookings.return_value = paginated_response
        
        # Execute
        response = client.get("/bookings/user?status=upcoming")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "booked"
        assert data["total"] == 1
        
        # Verify service was called with filter
        mock_booking_service.get_user_bookings.assert_called_once()
    
    def test_get_user_bookings_past_filter(self, client, mock_booking_service, sample_booking_list):
        """Test retrieval of past bookings."""
        # Filter to cancelled bookings (representing past)
        past_bookings = [b for b in sample_booking_list if b.status == "cancelled"]
        
        # Setup mock with PaginatedResponse
        paginated_response = PaginatedResponse(
            items=past_bookings,
            total=len(past_bookings),
            page=1,
            size=10,
            pages=1
        )
        mock_booking_service.get_user_bookings.return_value = paginated_response
        
        # Execute
        response = client.get("/bookings/user?status=past")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "cancelled"
        assert data["total"] == 1
        
        # Verify service was called with filter
        mock_booking_service.get_user_bookings.assert_called_once()
    
    def test_get_user_bookings_internal_error(self, client, mock_booking_service):
        """Test user bookings retrieval with internal error."""
        # Setup mock
        mock_booking_service.get_user_bookings.side_effect = Exception("Database connection failed")
        
        # Execute
        response = client.get("/bookings/user")
        
        # Verify
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Error retrieving bookings" in data["detail"]
    
    # ===== AUTHENTICATION TESTS =====
    
    def test_create_booking_without_authentication(self):
        """Test creating booking without authentication."""
        # Create app without authentication override
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.post("/bookings", json={"flight_id": 1})
        # This would normally return 401 or 403, but since we're not testing the actual auth middleware,
        # we expect a 403 error due to missing authentication
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_booking_without_authentication(self):
        """Test updating booking without authentication."""
        # Create app without authentication override
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.patch("/bookings/1", json={"status": "cancelled"})
        # This would normally return 401 or 403, but since we're not testing the actual auth middleware,
        # we expect a 403 error due to missing authentication
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_delete_booking_without_authentication(self):
        """Test deleting booking without authentication."""
        # Create app without authentication override
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.delete("/bookings/1")
        # This would normally return 401 or 403, but since we're not testing the actual auth middleware,
        # we expect a 403 error due to missing authentication
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_user_bookings_without_authentication(self):
        """Test getting user bookings without authentication."""
        # Create app without authentication override
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        response = client.get("/bookings/user")
        # This would normally return 401 or 403, but since we're not testing the actual auth middleware,
        # we expect a 403 error due to missing authentication
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_authenticated_user_passed_to_service(self, client, mock_booking_service, sample_booking_create_data, sample_booking_response, mock_current_user):
        """Test that authenticated user is properly passed to service methods."""
        # Setup mock
        mock_booking_service.create_booking.return_value = sample_booking_response
        
        # Execute
        response = client.post("/bookings", json=sample_booking_create_data)
        
        # Verify response
        assert response.status_code == status.HTTP_200_OK
        
        # Verify that the service was called with the correct user
        mock_booking_service.create_booking.assert_called_once()
        call_args = mock_booking_service.create_booking.call_args
        assert call_args[0][0] == mock_current_user  # First argument should be the user
    
    def test_authenticated_user_in_all_endpoints(self, client, mock_booking_service, mock_current_user, sample_booking_response, sample_cancelled_booking_response):
        """Test that all endpoints receive the authenticated user."""
        # Mock returns for different operations
        mock_booking_service.create_booking.return_value = sample_booking_response
        mock_booking_service.update_booking.return_value = sample_cancelled_booking_response
        mock_booking_service.delete_booking.return_value = {"message": "success"}
        paginated_response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=0
        )
        mock_booking_service.get_user_bookings.return_value = paginated_response
        
        # Test create booking endpoint
        client.post("/bookings", json={"flight_id": 1})
        mock_booking_service.create_booking.assert_called()
        create_call_args = mock_booking_service.create_booking.call_args
        assert create_call_args[0][0] == mock_current_user
        
        # Test update booking endpoint
        client.patch("/bookings/1", json={"status": "cancelled"})
        mock_booking_service.update_booking.assert_called()
        update_call_args = mock_booking_service.update_booking.call_args
        assert update_call_args[0][0] == mock_current_user
        
        # Test delete booking endpoint
        client.delete("/bookings/1")
        mock_booking_service.delete_booking.assert_called()
        delete_call_args = mock_booking_service.delete_booking.call_args
        assert delete_call_args[0][0] == mock_current_user
        
        # Test get user bookings endpoint
        client.get("/bookings/user")
        mock_booking_service.get_user_bookings.assert_called()
        get_call_args = mock_booking_service.get_user_bookings.call_args
        assert get_call_args[0][0] == mock_current_user
    
    def test_different_user_contexts(self, mock_booking_service):
        """Test that different user contexts are properly handled."""
        # Create a different user
        different_user = User(
            id=2,
            name="Jane Doe",
            email="jane.doe@example.com",
            password_hash="different_hash",
            phone="+9876543210"
        )
        
        # Create app with different user override
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[create_booking_service] = lambda: mock_booking_service
        app.dependency_overrides[get_current_user] = lambda: different_user
        
        client = TestClient(app)
        
        # Mock service response
        paginated_response = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            size=10,
            pages=0
        )
        mock_booking_service.get_user_bookings.return_value = paginated_response
        
        # Execute request
        response = client.get("/bookings/user")
        
        # Verify that the different user was passed to the service
        assert response.status_code == status.HTTP_200_OK
        mock_booking_service.get_user_bookings.assert_called()
        call_args = mock_booking_service.get_user_bookings.call_args
        assert call_args[0][0].id == 2
        assert call_args[0][0].email == "jane.doe@example.com"
    
    # ===== EDGE CASES =====
    
    def test_create_booking_zero_flight_id(self, client, mock_booking_service):
        """Test booking creation with zero flight_id."""
        # Setup mock to handle edge case
        mock_booking_service.create_booking.side_effect = FlightNotAvailableError(0)
        
        # Execute
        response = client.post("/bookings", json={"flight_id": 0})
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["error_code"] == "FLIGHT_NOT_AVAILABLE"
    
    def test_create_booking_negative_flight_id(self, client, mock_booking_service):
        """Test booking creation with negative flight_id."""
        # Setup mock to handle edge case
        mock_booking_service.create_booking.side_effect = FlightNotAvailableError(-1)
        
        # Execute
        response = client.post("/bookings", json={"flight_id": -1})
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["error_code"] == "FLIGHT_NOT_AVAILABLE"
    
    def test_update_booking_extreme_booking_id(self, client, mock_booking_service):
        """Test booking update with very large booking_id."""
        large_id = 999999999
        mock_booking_service.update_booking.side_effect = BookingNotFoundError(large_id)
        
        response = client.patch(f"/bookings/{large_id}", json={"status": "cancelled"})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["details"]["booking_id"] == large_id
