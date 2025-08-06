"""
Tests for BookingService - Service Layer
Tests mock the repository layer to focus on business logic.
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.booking import BookingBusinessService
from repository.booking import BookingRepository
from repository.flight import FlightRepository
from models import Booking, User, Flight
from schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from schemas.flight import PaginatedResponse
from exceptions import (
    FlightNotAvailableError, 
    BookingAlreadyExistsError, 
    BookingNotFoundError,
    AccessDeniedError,
    BookingCannotBeCancelledError,
    PastFlightCannotBeCancelledError
)


class TestBookingService:
    """Test suite for BookingService with mocked dependencies."""
    
    @pytest.fixture
    def mock_booking_repo(self):
        """Create a mock BookingRepository."""
        return Mock(spec=BookingRepository)
    
    @pytest.fixture
    def mock_flight_repo(self):
        """Create a mock FlightRepository."""
        return Mock(spec=FlightRepository)
    
    @pytest.fixture
    def booking_service(self, mock_booking_repo, mock_flight_repo):
        """Create BookingService instance with mocked dependencies."""
        return BookingBusinessService(mock_booking_repo, mock_flight_repo)
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user."""
        return User(
            id=1,
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
            phone="+1234567890"
        )
    
    @pytest.fixture
    def sample_user_2(self):
        """Create a second sample user."""
        return User(
            id=2,
            name="Jane Smith",
            email="jane.smith@example.com",
            password_hash="hashed_password_2",
            phone="+1234567891"
        )
    
    @pytest.fixture
    def sample_booking_create(self):
        """Create sample booking creation data."""
        return BookingCreate(flight_id=1)
    
    @pytest.fixture
    def sample_booking_update_cancel(self):
        """Create sample booking update data for cancellation."""
        return BookingUpdate(status="cancelled")
    
    @pytest.fixture
    def sample_booking_update_pending(self):
        """Create sample booking update data for pending status."""
        return BookingUpdate(status="pending")
    
    @pytest.fixture
    def sample_future_flight(self):
        """Create a sample future flight."""
        return Flight(
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
    def sample_past_flight(self):
        """Create a sample past flight."""
        return Flight(
            id=2,
            origin="Boston",
            destination="Miami",
            departure_time=datetime(2023, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2023, 1, 1, 13, 30, 0, tzinfo=timezone.utc),
            airline="Delta Airlines",
            price=350,
            status="completed"
        )
    
    @pytest.fixture
    def sample_db_booking(self, sample_user, sample_future_flight):
        """Create a sample booking from database."""
        return Booking(
            id=1,
            user_id=sample_user.id,
            flight_id=sample_future_flight.id,
            status="booked",
            booked_at=datetime.now(timezone.utc),
            cancelled_at=None,
            user=sample_user,
            flight=sample_future_flight
        )
    
    @pytest.fixture
    def sample_cancelled_booking(self, sample_user, sample_future_flight):
        """Create a sample cancelled booking."""
        return Booking(
            id=2,
            user_id=sample_user.id,
            flight_id=sample_future_flight.id,
            status="cancelled",
            booked_at=datetime.now(timezone.utc) - timedelta(hours=2),
            cancelled_at=datetime.now(timezone.utc) - timedelta(hours=1),
            user=sample_user,
            flight=sample_future_flight
        )
    
    @pytest.fixture
    def sample_booking_list(self, sample_user, sample_future_flight):
        """Create a list of sample bookings."""
        return [
            Booking(
                id=1,
                user_id=sample_user.id,
                flight_id=sample_future_flight.id,
                status="booked",
                booked_at=datetime.now(timezone.utc),
                cancelled_at=None,
                user=sample_user,
                flight=sample_future_flight
            ),
            Booking(
                id=2,
                user_id=sample_user.id,
                flight_id=2,
                status="cancelled",
                booked_at=datetime.now(timezone.utc) - timedelta(hours=1),
                cancelled_at=datetime.now(timezone.utc) - timedelta(minutes=30),
                user=sample_user,
                flight=Flight(id=2, origin="Chicago", destination="Seattle", 
                            departure_time=datetime(2025, 12, 26, 15, 0, 0, tzinfo=timezone.utc),
                            arrival_time=datetime(2025, 12, 26, 18, 30, 0, tzinfo=timezone.utc),
                            airline="United Airlines", price=450, status="scheduled")
            )
        ]
    
    # ===== CREATE BOOKING TESTS =====
    
    def test_create_booking_success(self, booking_service, mock_booking_repo, mock_flight_repo, 
                                  sample_user, sample_booking_create, sample_future_flight, sample_db_booking):
        """Test successful booking creation."""
        # Setup mocks
        mock_flight_repo.find_available_by_id.return_value = sample_future_flight
        mock_booking_repo.find_existing_booking.return_value = None
        mock_booking_repo.create.return_value = sample_db_booking
        
        # Execute
        result = booking_service.create_booking(sample_user, sample_booking_create)
        
        # Verify - now expecting BookingResponse object
        assert isinstance(result, BookingResponse)
        assert result.id == 1
        assert result.status == "booked"
        assert result.flight_id == 1
        assert result.flight.id == 1
        assert result.flight.origin == "New York"
        assert result.flight.destination == "Los Angeles"
        
        # Verify repository calls
        mock_flight_repo.find_available_by_id.assert_called_once_with(1)
        mock_booking_repo.find_existing_booking.assert_called_once_with(sample_user.id, 1)
        mock_booking_repo.create.assert_called_once_with(sample_user.id, 1)
    
    def test_create_booking_flight_not_available(self, booking_service, mock_flight_repo, 
                                               sample_user, sample_booking_create):
        """Test booking creation when flight is not available."""
        # Setup mock
        mock_flight_repo.find_available_by_id.return_value = None
        
        # Execute and verify exception
        with pytest.raises(FlightNotAvailableError) as exc_info:
            booking_service.create_booking(sample_user, sample_booking_create)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "FLIGHT_NOT_AVAILABLE"
        assert exc_info.value.details["flight_id"] == 1
        
        # Verify repository calls
        mock_flight_repo.find_available_by_id.assert_called_once_with(1)
    
    def test_create_booking_already_exists(self, booking_service, mock_booking_repo, mock_flight_repo,
                                         sample_user, sample_booking_create, sample_future_flight, sample_db_booking):
        """Test booking creation when user already has booking for flight."""
        # Setup mocks
        mock_flight_repo.find_available_by_id.return_value = sample_future_flight
        mock_booking_repo.find_existing_booking.return_value = sample_db_booking
        
        # Execute and verify exception
        with pytest.raises(BookingAlreadyExistsError) as exc_info:
            booking_service.create_booking(sample_user, sample_booking_create)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "BOOKING_ALREADY_EXISTS"
        assert exc_info.value.details["user_id"] == sample_user.id
        assert exc_info.value.details["flight_id"] == 1
        
        # Verify repository calls
        mock_flight_repo.find_available_by_id.assert_called_once_with(1)
        mock_booking_repo.find_existing_booking.assert_called_once_with(sample_user.id, 1)
        mock_booking_repo.create.assert_not_called()
    
    # ===== UPDATE BOOKING TESTS =====
    
    def test_update_booking_cancel_success(self, booking_service, mock_booking_repo, mock_flight_repo,
                                         sample_user, sample_booking_update_cancel, sample_db_booking, sample_future_flight):
        """Test successful booking cancellation."""
        # Setup mocks
        mock_booking_repo.find_by_id.return_value = sample_db_booking
        mock_flight_repo.find_by_id.return_value = sample_future_flight
        
        # Create updated booking without using **__dict__ which includes SQLAlchemy internal attributes
        updated_booking = Booking(
            id=sample_db_booking.id,
            user_id=sample_db_booking.user_id,
            flight_id=sample_db_booking.flight_id,
            status="cancelled",
            booked_at=sample_db_booking.booked_at,
            cancelled_at=datetime.now(timezone.utc),
            user=sample_db_booking.user,
            flight=sample_db_booking.flight
        )
        mock_booking_repo.update_status.return_value = updated_booking
        
        # Execute
        result = booking_service.update_booking(sample_user, 1, sample_booking_update_cancel)
        
        # Verify - now expecting BookingResponse object
        assert isinstance(result, BookingResponse)
        assert result.status == "cancelled"
        assert result.cancelled_at is not None
        
        # Verify repository calls
        mock_booking_repo.find_by_id.assert_called_once_with(1)
        mock_flight_repo.find_by_id.assert_called_once_with(sample_db_booking.flight_id)
        mock_booking_repo.update_status.assert_called_once()
    
    def test_update_booking_not_found(self, booking_service, mock_booking_repo, sample_user, sample_booking_update_cancel):
        """Test updating non-existent booking."""
        # Setup mock
        mock_booking_repo.find_by_id.return_value = None
        
        # Execute and verify exception
        with pytest.raises(BookingNotFoundError) as exc_info:
            booking_service.update_booking(sample_user, 999, sample_booking_update_cancel)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "BOOKING_NOT_FOUND"
        assert exc_info.value.details["booking_id"] == 999
        
        # Verify repository calls
        mock_booking_repo.find_by_id.assert_called_once_with(999)
    
    def test_update_booking_access_denied(self, booking_service, mock_booking_repo, sample_user_2, 
                                        sample_booking_update_cancel, sample_db_booking):
        """Test updating booking that belongs to different user."""
        # Setup mock
        mock_booking_repo.find_by_id.return_value = sample_db_booking
        
        # Execute and verify exception
        with pytest.raises(AccessDeniedError) as exc_info:
            booking_service.update_booking(sample_user_2, 1, sample_booking_update_cancel)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "ACCESS_DENIED"
        assert exc_info.value.details["resource_type"] == "booking"
        assert exc_info.value.details["resource_id"] == 1
        assert exc_info.value.details["user_id"] == sample_user_2.id
        
        # Verify repository calls
        mock_booking_repo.find_by_id.assert_called_once_with(1)
    
    def test_update_booking_cancel_past_flight(self, booking_service, mock_booking_repo, mock_flight_repo,
                                             sample_user, sample_booking_update_cancel, sample_past_flight):
        """Test cancelling booking for past flight."""
        # Setup booking for past flight
        past_booking = Booking(
            id=1,
            user_id=sample_user.id,
            flight_id=sample_past_flight.id,
            status="booked",
            booked_at=datetime.now(timezone.utc),
            cancelled_at=None,
            user=sample_user,
            flight=sample_past_flight
        )
        
        # Setup mocks
        mock_booking_repo.find_by_id.return_value = past_booking
        mock_flight_repo.find_by_id.return_value = sample_past_flight
        
        # Execute and verify exception
        with pytest.raises(PastFlightCannotBeCancelledError) as exc_info:
            booking_service.update_booking(sample_user, 1, sample_booking_update_cancel)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "PAST_FLIGHT_CANNOT_BE_CANCELLED"
        assert exc_info.value.details["booking_id"] == 1
        assert exc_info.value.details["flight_id"] == sample_past_flight.id
    
    def test_update_booking_non_cancel_status(self, booking_service, mock_booking_repo,
                                            sample_user, sample_booking_update_pending, sample_db_booking):
        """Test updating booking to non-cancel status."""
        # Setup mocks
        mock_booking_repo.find_by_id.return_value = sample_db_booking
        
        # Create updated booking without using **__dict__
        updated_booking = Booking(
            id=sample_db_booking.id,
            user_id=sample_db_booking.user_id,
            flight_id=sample_db_booking.flight_id,
            status="pending",
            booked_at=sample_db_booking.booked_at,
            cancelled_at=sample_db_booking.cancelled_at,
            user=sample_db_booking.user,
            flight=sample_db_booking.flight
        )
        mock_booking_repo.update_status.return_value = updated_booking
        
        # Execute
        result = booking_service.update_booking(sample_user, 1, sample_booking_update_pending)
        
        # Verify - now expecting BookingResponse object
        # Note: The computed status logic will convert "pending" to "booked" for future flights
        assert isinstance(result, BookingResponse)
        assert result.status == "booked"  # Updated to match computed status logic
        
        # Verify repository calls
        mock_booking_repo.find_by_id.assert_called_once_with(1)
        mock_booking_repo.update_status.assert_called_once_with(1, "pending")
    
    # ===== DELETE BOOKING TESTS =====
    
    def test_delete_booking_success(self, booking_service, mock_booking_repo, mock_flight_repo,
                                  sample_user, sample_db_booking, sample_future_flight):
        """Test successful booking deletion."""
        # Setup mocks
        mock_booking_repo.find_by_id.return_value = sample_db_booking
        mock_flight_repo.find_by_id.return_value = sample_future_flight
        mock_booking_repo.update_status.return_value = sample_db_booking
        
        # Execute
        result = booking_service.delete_booking(sample_user, 1)
        
        # Verify
        assert result == {"message": "Booking cancelled successfully"}
        
        # Verify repository calls
        mock_booking_repo.find_by_id.assert_called_once_with(1)
        mock_flight_repo.find_by_id.assert_called_once_with(sample_db_booking.flight_id)
        mock_booking_repo.update_status.assert_called_once()
    
    def test_delete_booking_not_found(self, booking_service, mock_booking_repo, sample_user):
        """Test deleting non-existent booking."""
        # Setup mock
        mock_booking_repo.find_by_id.return_value = None
        
        # Execute and verify exception
        with pytest.raises(BookingNotFoundError) as exc_info:
            booking_service.delete_booking(sample_user, 999)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "BOOKING_NOT_FOUND"
        assert exc_info.value.details["booking_id"] == 999
    
    def test_delete_booking_access_denied(self, booking_service, mock_booking_repo, sample_user_2, sample_db_booking):
        """Test deleting booking that belongs to different user."""
        # Setup mock
        mock_booking_repo.find_by_id.return_value = sample_db_booking
        
        # Execute and verify exception
        with pytest.raises(AccessDeniedError) as exc_info:
            booking_service.delete_booking(sample_user_2, 1)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "ACCESS_DENIED"
        assert exc_info.value.details["resource_type"] == "booking"
        assert exc_info.value.details["resource_id"] == 1
        assert exc_info.value.details["user_id"] == sample_user_2.id
    
    def test_delete_booking_already_cancelled(self, booking_service, mock_booking_repo, sample_user, sample_cancelled_booking):
        """Test deleting already cancelled booking."""
        # Setup mock
        mock_booking_repo.find_by_id.return_value = sample_cancelled_booking
        
        # Execute and verify exception
        with pytest.raises(BookingCannotBeCancelledError) as exc_info:
            booking_service.delete_booking(sample_user, 1)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "BOOKING_CANNOT_BE_CANCELLED"
        assert exc_info.value.details["booking_id"] == 1
        assert exc_info.value.details["current_status"] == "cancelled"
    
    def test_delete_booking_past_flight(self, booking_service, mock_booking_repo, mock_flight_repo,
                                      sample_user, sample_past_flight):
        """Test deleting booking for past flight."""
        # Setup booking for past flight
        past_booking = Booking(
            id=1,
            user_id=sample_user.id,
            flight_id=sample_past_flight.id,
            status="booked",
            booked_at=datetime.now(timezone.utc),
            cancelled_at=None,
            user=sample_user,
            flight=sample_past_flight
        )
        
        # Setup mocks
        mock_booking_repo.find_by_id.return_value = past_booking
        mock_flight_repo.find_by_id.return_value = sample_past_flight
        
        # Execute and verify exception
        with pytest.raises(PastFlightCannotBeCancelledError) as exc_info:
            booking_service.delete_booking(sample_user, 1)
        
        # Verify exception details
        assert exc_info.value.error_code.value == "PAST_FLIGHT_CANNOT_BE_CANCELLED"
        assert exc_info.value.details["booking_id"] == 1
        assert exc_info.value.details["flight_id"] == sample_past_flight.id
    
    # ===== GET USER BOOKINGS TESTS =====
    
    def test_get_user_bookings_success(self, booking_service, mock_booking_repo, sample_user, sample_booking_list):
        """Test successful retrieval of user bookings."""
        # Setup mock to return tuple (bookings, total_count)
        mock_booking_repo.find_by_user_id_paginated.return_value = (sample_booking_list, 2)
        
        # Execute
        result = booking_service.get_user_bookings(sample_user)
        
        # Verify - now expecting PaginatedResponse object
        assert isinstance(result, PaginatedResponse)
        assert result.total == 2
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1
        assert len(result.items) == 2
        assert isinstance(result.items[0], BookingResponse)
        assert result.items[0].id == 1
        assert result.items[0].status == "booked"
        assert isinstance(result.items[1], BookingResponse)
        assert result.items[1].id == 2
        assert result.items[1].status == "cancelled"
        
        # Verify repository calls
        mock_booking_repo.find_by_user_id_paginated.assert_called_once_with(sample_user.id, None, None, None, 1, 10)
    
    def test_get_user_bookings_with_status_filter(self, booking_service, mock_booking_repo, sample_user, sample_booking_list):
        """Test retrieval of user bookings with status filter."""
        # Filter to only booked bookings
        booked_bookings = [b for b in sample_booking_list if b.status == "booked"]
        
        # Setup mock to return tuple (bookings, total_count)
        mock_booking_repo.find_by_user_id_paginated.return_value = (booked_bookings, 1)
        
        # Execute
        result = booking_service.get_user_bookings(sample_user, "booked")
        
        # Verify - now expecting PaginatedResponse object
        assert isinstance(result, PaginatedResponse)
        assert result.total == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], BookingResponse)
        assert result.items[0].status == "booked"
        
        # Verify repository calls
        mock_booking_repo.find_by_user_id_paginated.assert_called_once_with(sample_user.id, "booked", None, None, 1, 10)
    
    def test_get_user_bookings_empty(self, booking_service, mock_booking_repo, sample_user):
        """Test retrieval of user bookings when user has no bookings."""
        # Setup mock to return tuple (empty list, 0 count)
        mock_booking_repo.find_by_user_id_paginated.return_value = ([], 0)
        
        # Execute
        result = booking_service.get_user_bookings(sample_user)
        
        # Verify - now expecting PaginatedResponse object
        assert isinstance(result, PaginatedResponse)
        assert result.total == 0
        assert len(result.items) == 0
        
        # Verify repository calls
        mock_booking_repo.find_by_user_id_paginated.assert_called_once_with(sample_user.id, None, None, None, 1, 10)
    
    def test_get_user_bookings_upcoming_filter(self, booking_service, mock_booking_repo, sample_user, sample_booking_list):
        """Test retrieval of upcoming bookings."""
        # Filter to only upcoming bookings
        upcoming_bookings = [b for b in sample_booking_list if b.status == "booked"]
        
        # Setup mock to return tuple (bookings, total_count)
        mock_booking_repo.find_by_user_id_paginated.return_value = (upcoming_bookings, 1)
        
        # Execute
        result = booking_service.get_user_bookings(sample_user, "upcoming")
        
        # Verify - now expecting PaginatedResponse object
        assert isinstance(result, PaginatedResponse)
        assert result.total == 1
        assert len(result.items) == 1
        assert isinstance(result.items[0], BookingResponse)
        
        # Verify repository calls
        mock_booking_repo.find_by_user_id_paginated.assert_called_once_with(sample_user.id, "upcoming", None, None, 1, 10)
    
    # ===== EDGE CASES =====
    
    def test_create_booking_repository_error(self, booking_service, mock_booking_repo, mock_flight_repo,
                                           sample_user, sample_booking_create, sample_future_flight):
        """Test booking creation with repository error."""
        # Setup mocks
        mock_flight_repo.find_available_by_id.return_value = sample_future_flight
        mock_booking_repo.find_existing_booking.return_value = None
        mock_booking_repo.create.side_effect = Exception("Database connection failed")
        
        # Execute and verify exception
        with pytest.raises(Exception) as exc_info:
            booking_service.create_booking(sample_user, sample_booking_create)
        
        assert "Database connection failed" in str(exc_info.value)
    
    def test_get_user_bookings_repository_error(self, booking_service, mock_booking_repo, sample_user):
        """Test user bookings retrieval with repository error."""
        # Setup mock to raise exception
        mock_booking_repo.find_by_user_id_paginated.side_effect = Exception("Database connection failed")
        
        # Execute and verify exception
        with pytest.raises(Exception) as exc_info:
            booking_service.get_user_bookings(sample_user)
        
        assert "Database connection failed" in str(exc_info.value)
