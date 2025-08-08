"""
Tests for BookingRepository - Repository Layer
Tests use in-memory SQLite database to ensure data isolation.
"""
import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Base, Booking, User, Flight
from repository.booking import BookingSqliteRepository


class TestBookingRepository:
    """Test suite for BookingRepository using in-memory SQLite database."""
    
    @pytest.fixture
    def db_session(self):
        """Create an in-memory SQLite database session for testing."""
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture
    def booking_repo(self, db_session):
        """Create BookingRepository instance."""
        return BookingSqliteRepository(db_session)
    
    @pytest.fixture
    def sample_user(self, db_session):
        """Create a sample user in the database."""
        user = User(
            name="John Doe",
            email="john.doe@example.com",
            password_hash="hashed_password",
            phone="+1234567890"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def sample_user_2(self, db_session):
        """Create a second sample user in the database."""
        user = User(
            name="Jane Smith",
            email="jane.smith@example.com",
            password_hash="hashed_password_2",
            phone="+1234567891"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user
    
    @pytest.fixture
    def sample_flight(self, db_session):
        """Create a sample flight in the database."""
        flight = Flight(
            origin="New York",
            destination="Los Angeles",
            departure_time=datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc),
            airline="American Airlines",
            price=299,
            status="scheduled"
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        return flight
    
    @pytest.fixture
    def sample_flight_2(self, db_session):
        """Create a second sample flight in the database."""
        flight = Flight(
            origin="Chicago",
            destination="Seattle",
            departure_time=datetime(2025, 12, 26, 15, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 26, 18, 30, 0, tzinfo=timezone.utc),
            airline="United Airlines",
            price=450,
            status="scheduled"
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        return flight
    
    @pytest.fixture
    def past_flight(self, db_session):
        """Create a past flight in the database."""
        flight = Flight(
            origin="Boston",
            destination="Miami",
            departure_time=datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 1, 1, 13, 30, 0, tzinfo=timezone.utc),
            airline="Delta Airlines",
            price=350,
            status="completed"
        )
        db_session.add(flight)
        db_session.commit()
        db_session.refresh(flight)
        return flight
    
    # ===== POSITIVE TESTS =====
    
    def test_create_booking_success(self, booking_repo, sample_user, sample_flight):
        """Test successful booking creation."""
        booking = booking_repo.create(sample_user.id, sample_flight.id)
        
        assert booking.id is not None
        assert booking.user_id == sample_user.id
        assert booking.flight_id == sample_flight.id
        assert booking.status == "booked"
        assert booking.booked_at is not None
        assert booking.cancelled_at is None
    
    def test_create_booking_with_custom_status(self, booking_repo, sample_user, sample_flight):
        """Test booking creation with custom status."""
        booking = booking_repo.create(sample_user.id, sample_flight.id, "pending")
        
        assert booking.id is not None
        assert booking.status == "pending"
        assert booking.user_id == sample_user.id
        assert booking.flight_id == sample_flight.id
    
    def test_find_by_id_success(self, booking_repo, sample_user, sample_flight):
        """Test finding booking by ID when booking exists."""
        created_booking = booking_repo.create(sample_user.id, sample_flight.id)
        found_booking = booking_repo.find_by_id(created_booking.id)
        
        assert found_booking is not None
        assert found_booking.id == created_booking.id
        assert found_booking.user_id == sample_user.id
        assert found_booking.flight_id == sample_flight.id
        assert found_booking.status == "booked"
    
    def test_find_existing_booking_success(self, booking_repo, sample_user, sample_flight):
        """Test finding existing active booking for user and flight."""
        created_booking = booking_repo.create(sample_user.id, sample_flight.id)
        existing_booking = booking_repo.find_existing_booking(sample_user.id, sample_flight.id)
        
        assert existing_booking is not None
        assert existing_booking.id == created_booking.id
        assert existing_booking.status == "booked"
    
    def test_update_status_success(self, booking_repo, sample_user, sample_flight):
        """Test successful status update."""
        booking = booking_repo.create(sample_user.id, sample_flight.id)
        cancelled_time = datetime.now(timezone.utc)
        
        updated_booking = booking_repo.update_status(booking.id, "cancelled", cancelled_time)
        
        assert updated_booking.id == booking.id
        assert updated_booking.status == "cancelled"
        
        # Handle timezone differences - if stored datetime is naive, assume UTC
        actual_cancelled_at = updated_booking.cancelled_at
        if actual_cancelled_at.tzinfo is None:
            actual_cancelled_at = actual_cancelled_at.replace(tzinfo=timezone.utc)
        assert actual_cancelled_at == cancelled_time
    
    def test_update_status_without_cancelled_at(self, booking_repo, sample_user, sample_flight):
        """Test status update without cancelled_at timestamp."""
        booking = booking_repo.create(sample_user.id, sample_flight.id)
        
        updated_booking = booking_repo.update_status(booking.id, "pending")
        
        assert updated_booking.status == "pending"
        assert updated_booking.cancelled_at is None
    
    def test_find_by_user_id_success(self, booking_repo, sample_user, sample_flight, sample_flight_2):
        """Test finding all bookings for a user."""
        booking1 = booking_repo.create(sample_user.id, sample_flight.id)
        booking2 = booking_repo.create(sample_user.id, sample_flight_2.id)
        
        user_bookings = booking_repo.find_by_user_id(sample_user.id)
        
        assert len(user_bookings) == 2
        booking_ids = [b.id for b in user_bookings]
        assert booking1.id in booking_ids
        assert booking2.id in booking_ids
    
    def test_find_by_user_id_with_status_filter(self, booking_repo, sample_user, sample_flight, sample_flight_2):
        """Test finding bookings for a user with status filter."""
        booking1 = booking_repo.create(sample_user.id, sample_flight.id)
        booking2 = booking_repo.create(sample_user.id, sample_flight_2.id)
        booking_repo.update_status(booking2.id, "cancelled")
        
        booked_bookings = booking_repo.find_by_user_id(sample_user.id, "booked")
        cancelled_bookings = booking_repo.find_by_user_id(sample_user.id, "cancelled")
        
        assert len(booked_bookings) == 1
        assert booked_bookings[0].id == booking1.id
        assert len(cancelled_bookings) == 1
        assert cancelled_bookings[0].id == booking2.id
    
    def test_find_by_user_id_upcoming_filter(self, booking_repo, sample_user, sample_flight, past_flight):
        """Test finding upcoming bookings."""
        future_booking = booking_repo.create(sample_user.id, sample_flight.id)
        past_booking = booking_repo.create(sample_user.id, past_flight.id)
        
        upcoming_bookings = booking_repo.find_by_user_id(sample_user.id, "upcoming")
        
        assert len(upcoming_bookings) == 1
        assert upcoming_bookings[0].id == future_booking.id
    
    def test_find_by_user_id_past_filter(self, booking_repo, sample_user, sample_flight, past_flight):
        """Test finding past bookings."""
        future_booking = booking_repo.create(sample_user.id, sample_flight.id)
        past_booking = booking_repo.create(sample_user.id, past_flight.id)
        cancelled_booking = booking_repo.create(sample_user.id, sample_flight.id)
        booking_repo.update_status(cancelled_booking.id, "cancelled")
        
        past_bookings = booking_repo.find_by_user_id(sample_user.id, "past")
        
        assert len(past_bookings) == 2
        booking_ids = [b.id for b in past_bookings]
        assert past_booking.id in booking_ids
        assert cancelled_booking.id in booking_ids
    
    def test_delete_by_id_success(self, booking_repo, sample_user, sample_flight):
        """Test successful booking deletion."""
        booking = booking_repo.create(sample_user.id, sample_flight.id)
        
        result = booking_repo.delete_by_id(booking.id)
        
        assert result is True
        # Verify booking is deleted
        deleted_booking = booking_repo.find_by_id(booking.id)
        assert deleted_booking is None
    
    # ===== NEGATIVE TESTS =====
    
    def test_find_by_id_not_found(self, booking_repo):
        """Test finding booking by ID when booking doesn't exist."""
        found_booking = booking_repo.find_by_id(999)
        assert found_booking is None
    
    def test_find_existing_booking_not_found(self, booking_repo, sample_user, sample_flight):
        """Test finding existing booking when none exists."""
        existing_booking = booking_repo.find_existing_booking(sample_user.id, sample_flight.id)
        assert existing_booking is None
    
    def test_find_existing_booking_only_active(self, booking_repo, sample_user, sample_flight):
        """Test that find_existing_booking only returns active bookings."""
        booking = booking_repo.create(sample_user.id, sample_flight.id)
        booking_repo.update_status(booking.id, "cancelled")
        
        existing_booking = booking_repo.find_existing_booking(sample_user.id, sample_flight.id)
        assert existing_booking is None
    
    def test_update_status_booking_not_found(self, booking_repo):
        """Test updating status of non-existent booking."""
        with pytest.raises(ValueError) as exc_info:
            booking_repo.update_status(999, "cancelled")
        
        assert "Booking with ID 999 not found" in str(exc_info.value)
    
    def test_find_by_user_id_empty(self, booking_repo, sample_user):
        """Test finding bookings for user with no bookings."""
        user_bookings = booking_repo.find_by_user_id(sample_user.id)
        assert len(user_bookings) == 0
    
    def test_find_by_user_id_different_user(self, booking_repo, sample_user, sample_user_2, sample_flight):
        """Test that bookings are isolated by user."""
        booking_repo.create(sample_user.id, sample_flight.id)
        
        user2_bookings = booking_repo.find_by_user_id(sample_user_2.id)
        assert len(user2_bookings) == 0
    
    def test_delete_by_id_not_found(self, booking_repo):
        """Test deleting non-existent booking."""
        result = booking_repo.delete_by_id(999)
        assert result is False
    
    # ===== EDGE CASES =====
    
    def test_create_multiple_bookings_same_user_different_flights(self, booking_repo, sample_user, sample_flight, sample_flight_2):
        """Test creating multiple bookings for same user on different flights."""
        booking1 = booking_repo.create(sample_user.id, sample_flight.id)
        booking2 = booking_repo.create(sample_user.id, sample_flight_2.id)
        
        assert booking1.id != booking2.id
        assert booking1.flight_id != booking2.flight_id
        assert booking1.user_id == booking2.user_id
    
    def test_create_multiple_bookings_different_users_same_flight(self, booking_repo, sample_user, sample_user_2, sample_flight):
        """Test creating bookings for different users on same flight."""
        booking1 = booking_repo.create(sample_user.id, sample_flight.id)
        booking2 = booking_repo.create(sample_user_2.id, sample_flight.id)
        
        assert booking1.id != booking2.id
        assert booking1.user_id != booking2.user_id
        assert booking1.flight_id == booking2.flight_id
    
    def test_status_filter_case_sensitivity(self, booking_repo, sample_user, sample_flight):
        """Test status filter case sensitivity."""
        booking_repo.create(sample_user.id, sample_flight.id)
        
        # Test exact match
        exact_bookings = booking_repo.find_by_user_id(sample_user.id, "booked")
        assert len(exact_bookings) == 1
        
        # Test case mismatch
        case_bookings = booking_repo.find_by_user_id(sample_user.id, "BOOKED")
        assert len(case_bookings) == 0
    
    def test_cancelled_at_precision(self, booking_repo, sample_user, sample_flight):
        """Test cancelled_at timestamp precision."""
        booking = booking_repo.create(sample_user.id, sample_flight.id)
        precise_time = datetime(2025, 8, 5, 12, 30, 45, 123456, tzinfo=timezone.utc)
        
        updated_booking = booking_repo.update_status(booking.id, "cancelled", precise_time)
        
        # Handle timezone differences - if stored datetime is naive, assume UTC
        actual_cancelled_at = updated_booking.cancelled_at
        if actual_cancelled_at.tzinfo is None:
            actual_cancelled_at = actual_cancelled_at.replace(tzinfo=timezone.utc)
        assert actual_cancelled_at == precise_time
    
    # ===== DEPENDENCY INJECTION TESTS =====
    
    def test_create_booking_repository_function(self):
        """Test the dependency injection function for creating booking repository."""
        from repository.booking import create_booking_repository
        from unittest.mock import Mock
        
        # Mock database session
        mock_db = Mock()
        
        # Test the function
        repo = create_booking_repository(mock_db)
        
        # Verify it returns the correct type
        from repository.booking import BookingSqliteRepository
        assert isinstance(repo, BookingSqliteRepository)
        assert repo.db == mock_db
