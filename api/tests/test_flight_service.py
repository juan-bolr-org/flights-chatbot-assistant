"""
Tests for FlightService - Service Layer
Tests mock the repository layer to focus on business logic.
"""
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.flight import FlightBusinessService
from repository.flight import FlightRepository
from models import Flight, User
from schemas.flight import FlightCreate, FlightSearch, FlightResponse, PaginatedResponse
from exceptions import InvalidDateFormatError, InvalidFlightTimesError, InvalidFlightPriceError, ErrorCode


class TestFlightService:
    """Test suite for FlightService with mocked dependencies."""
    
    @pytest.fixture
    def mock_flight_repo(self):
        """Create mock FlightRepository."""
        return Mock(spec=FlightRepository)
    
    @pytest.fixture
    def flight_service(self, mock_flight_repo):
        """Create FlightService instance with mocked repository."""
        return FlightBusinessService(mock_flight_repo)
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "john.doe@example.com"
        user.name = "John Doe"
        return user
    
    @pytest.fixture
    def sample_flight_create(self):
        """Create sample FlightCreate schema for testing."""
        return FlightCreate(
            origin="New York",
            destination="Los Angeles",
            departure_time=datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc),
            airline="American Airlines",
            price=299.99,
            status="scheduled"
        )
    
    @pytest.fixture
    def sample_flight_create_no_status(self):
        """Create sample FlightCreate without status for testing."""
        return FlightCreate(
            origin="Chicago",
            destination="Miami",
            departure_time=datetime(2025, 12, 26, 14, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 26, 17, 45, 0, tzinfo=timezone.utc),
            airline="Delta Airlines",
            price=399.50
        )
    
    @pytest.fixture
    def sample_db_flight(self):
        """Create sample Flight model for testing."""
        flight = Mock(spec=Flight)
        flight.id = 1
        flight.origin = "New York"
        flight.destination = "Los Angeles"
        flight.departure_time = datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc)
        flight.arrival_time = datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc)
        flight.airline = "American Airlines"
        flight.price = 299
        flight.status = "scheduled"
        return flight
    
    @pytest.fixture
    def sample_flight_list(self):
        """Create sample list of flights for testing."""
        flight1 = Mock(spec=Flight)
        flight1.id = 1
        flight1.origin = "New York"
        flight1.destination = "Los Angeles"
        flight1.departure_time = datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc)
        flight1.arrival_time = datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc)
        flight1.airline = "American Airlines"
        flight1.status = "scheduled"
        flight1.price = 299
        
        flight2 = Mock(spec=Flight)
        flight2.id = 2
        flight2.origin = "Chicago"
        flight2.destination = "Miami"
        flight2.departure_time = datetime(2025, 12, 26, 14, 0, 0, tzinfo=timezone.utc)
        flight2.arrival_time = datetime(2025, 12, 26, 17, 45, 0, tzinfo=timezone.utc)
        flight2.airline = "Delta Airlines"
        flight2.status = "scheduled"
        flight2.price = 399
        
        return [flight1, flight2]
    
    # ===== SEARCH FLIGHTS TESTS =====
    
    def test_search_flights_success(self, flight_service, mock_flight_repo, sample_flight_list):
        """Test successful flight search."""
        # Setup mock to return tuple (flights, total)
        mock_flight_repo.search_flights.return_value = (sample_flight_list, 2)
        
        # Execute
        result = flight_service.search_flights("New York", "Los Angeles", "2025-12-25")
        
        # Verify - now expecting PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1
        assert isinstance(result.items[0], FlightResponse)
        assert result.items[0].id == 1
        assert result.items[0].origin == "New York"
        assert result.items[0].destination == "Los Angeles"
        assert isinstance(result.items[1], FlightResponse)
        assert result.items[1].id == 2
        assert result.items[1].origin == "Chicago"
        assert result.items[1].destination == "Miami"
        
        # Verify repository call
        mock_flight_repo.search_flights.assert_called_once_with("New York", "Los Angeles", "2025-12-25", 1, 10)
    
    def test_search_flights_empty_result(self, flight_service, mock_flight_repo):
        """Test flight search with no results."""
        # Setup mock to return tuple (empty flights, total 0)
        mock_flight_repo.search_flights.return_value = ([], 0)
        
        # Execute
        result = flight_service.search_flights("Boston", "Seattle", "2025-12-25")
        
        # Verify - now expecting PaginatedResponse with empty items
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0
        assert result.total == 0
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1
        
        # Verify repository call
        mock_flight_repo.search_flights.assert_called_once_with("Boston", "Seattle", "2025-12-25", 1, 10)
    
    def test_search_flights_invalid_date_format(self, flight_service, mock_flight_repo):
        """Test flight search with invalid date format."""
        # Setup mock to raise ValueError
        mock_flight_repo.search_flights.side_effect = ValueError("Invalid date format")
        
        # Execute and verify exception
        with pytest.raises(InvalidDateFormatError) as exc_info:
            flight_service.search_flights("New York", "Los Angeles", "2025/12/25")
        
        # Verify exception details
        assert exc_info.value.error_code == ErrorCode.INVALID_DATE_FORMAT
        assert exc_info.value.details["provided_date"] == "2025/12/25"
        
        # Verify repository call
        mock_flight_repo.search_flights.assert_called_once_with("New York", "Los Angeles", "2025/12/25", 1, 10)
    
    def test_search_flights_case_handling(self, flight_service, mock_flight_repo, sample_flight_list):
        """Test flight search with different case inputs."""
        # Setup mock to return tuple (flights, total)
        mock_flight_repo.search_flights.return_value = (sample_flight_list, 2)
        
        # Execute with different case
        result = flight_service.search_flights("new york", "LOS ANGELES", "2025-12-25")
        
        # Verify - now expecting PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], FlightResponse)
        
        # Verify repository call preserves original case
        mock_flight_repo.search_flights.assert_called_once_with("new york", "LOS ANGELES", "2025-12-25", 1, 10)
    
    # ===== CREATE FLIGHT TESTS =====
    
    def test_create_flight_success(self, flight_service, mock_flight_repo, sample_user, sample_flight_create, sample_db_flight):
        """Test successful flight creation."""
        # Setup mock
        mock_flight_repo.create.return_value = sample_db_flight
        
        # Execute
        result = flight_service.create_flight(sample_user, sample_flight_create)
        
        # Verify - now expecting FlightResponse object
        assert isinstance(result, FlightResponse)
        assert result.id == 1
        assert result.origin == "New York"
        assert result.destination == "Los Angeles"
        assert result.airline == "American Airlines"
        assert result.price == 299
        assert result.status == "scheduled"
        
        # Verify repository call
        mock_flight_repo.create.assert_called_once_with(
            origin="New York",
            destination="Los Angeles",
            departure_time=sample_flight_create.departure_time,
            arrival_time=sample_flight_create.arrival_time,
            airline="American Airlines",
            price=299,  # Should be converted to int
            status="scheduled"
        )
    
    def test_create_flight_without_status(self, flight_service, mock_flight_repo, sample_user, sample_flight_create_no_status, sample_db_flight):
        """Test flight creation without status (uses default)."""
        # Setup mock
        mock_flight_repo.create.return_value = sample_db_flight
        
        # Execute
        result = flight_service.create_flight(sample_user, sample_flight_create_no_status)
        
        # Verify - now expecting FlightResponse object
        assert isinstance(result, FlightResponse)
        assert result.id == 1
        assert result.origin == "New York"
        assert result.destination == "Los Angeles"
        
        # Verify repository call with default status
        mock_flight_repo.create.assert_called_once_with(
            origin="Chicago",
            destination="Miami",
            departure_time=sample_flight_create_no_status.departure_time,
            arrival_time=sample_flight_create_no_status.arrival_time,
            airline="Delta Airlines",
            price=399,  # Should be converted to int
            status="scheduled"  # Default status
        )
    
    def test_create_flight_price_conversion(self, flight_service, mock_flight_repo, sample_user, sample_db_flight):
        """Test that float prices are converted to integers."""
        # Create flight with float price
        flight_create = FlightCreate(
            origin="Boston",
            destination="Seattle",
            departure_time=datetime(2025, 12, 27, 9, 0, 0, tzinfo=timezone.utc),
            arrival_time=datetime(2025, 12, 27, 12, 30, 0, tzinfo=timezone.utc),
            airline="Alaska Airlines",
            price=450.75,  # Float price
            status="scheduled"
        )
        
        # Setup mock
        mock_flight_repo.create.return_value = sample_db_flight
        
        # Execute
        result = flight_service.create_flight(sample_user, flight_create)
        
        # Verify repository call with integer price
        mock_flight_repo.create.assert_called_once_with(
            origin="Boston",
            destination="Seattle",
            departure_time=flight_create.departure_time,
            arrival_time=flight_create.arrival_time,
            airline="Alaska Airlines",
            price=450,  # Should be converted to int (truncated)
            status="scheduled"
        )
    
    def test_create_flight_repository_error(self, flight_service, mock_flight_repo, sample_user, sample_flight_create):
        """Test flight creation when repository raises error."""
        # Setup mock to raise exception
        mock_flight_repo.create.side_effect = Exception("Database connection failed")
        
        # Execute and verify exception propagates
        with pytest.raises(Exception, match="Database connection failed"):
            flight_service.create_flight(sample_user, sample_flight_create)
        
        # Verify repository was called
        mock_flight_repo.create.assert_called_once()
    
    # ===== LIST FLIGHTS TESTS =====
    
    def test_list_flights_success(self, flight_service, mock_flight_repo, sample_flight_list):
        """Test successful flight listing."""
        # Setup mock to return tuple (flights, total)
        mock_flight_repo.list_all.return_value = (sample_flight_list, 2)
        
        # Execute
        result = flight_service.list_flights()
        
        # Verify - now expecting PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1
        assert isinstance(result.items[0], FlightResponse)
        assert result.items[0].id == 1
        assert result.items[0].origin == "New York"
        assert isinstance(result.items[1], FlightResponse)
        assert result.items[1].id == 2
        assert result.items[1].origin == "Chicago"
        
        # Verify repository call
        mock_flight_repo.list_all.assert_called_once_with(1, 10)
    
    def test_list_flights_empty(self, flight_service, mock_flight_repo):
        """Test flight listing when no flights exist."""
        # Setup mock to return tuple (empty flights, total 0)
        mock_flight_repo.list_all.return_value = ([], 0)
        
        # Execute
        result = flight_service.list_flights()
        
        # Verify - now expecting PaginatedResponse with empty items
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0
        assert result.total == 0
        assert result.page == 1
        assert result.size == 10
        assert result.pages == 1
        
        # Verify repository call
        mock_flight_repo.list_all.assert_called_once_with(1, 10)
    
    def test_list_flights_repository_error(self, flight_service, mock_flight_repo):
        """Test flight listing when repository raises error."""
        # Setup mock to raise exception
        mock_flight_repo.list_all.side_effect = Exception("Database connection failed")
        
        # Execute and verify exception propagates
        with pytest.raises(Exception, match="Database connection failed"):
            flight_service.list_flights()
        
        # Verify repository was called
        mock_flight_repo.list_all.assert_called_once_with(1, 10)
    
    # ===== EDGE CASES =====
    
    def test_search_flights_with_special_characters(self, flight_service, mock_flight_repo, sample_flight_list):
        """Test flight search with special characters in city names."""
        # Setup mock to return tuple (flights, total)
        mock_flight_repo.search_flights.return_value = (sample_flight_list, 2)
        
        # Execute with special characters
        result = flight_service.search_flights("São Paulo", "México City", "2025-12-25")
        
        # Verify - now expecting PaginatedResponse
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert isinstance(result.items[0], FlightResponse)
        
        # Verify repository call preserves special characters
        mock_flight_repo.search_flights.assert_called_once_with("São Paulo", "México City", "2025-12-25", 1, 10)
    
    def test_create_flight_extreme_dates(self, flight_service, mock_flight_repo, sample_user, sample_db_flight):
        """Test flight creation with extreme future dates."""
        # Create flight far in the future
        future_flight = FlightCreate(
            origin="Mars Colony",
            destination="Earth Station",
            departure_time=datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
            arrival_time=datetime(2100, 1, 1, 6, 0, 0, tzinfo=timezone.utc),
            airline="SpaceX",
            price=999999.99,
            status="scheduled"
        )
        
        # Setup mock
        mock_flight_repo.create.return_value = sample_db_flight
        
        # Execute
        result = flight_service.create_flight(sample_user, future_flight)
        
        # Verify repository call
        mock_flight_repo.create.assert_called_once_with(
            origin="Mars Colony",
            destination="Earth Station",
            departure_time=future_flight.departure_time,
            arrival_time=future_flight.arrival_time,
            airline="SpaceX",
            price=999999,  # Converted to int
            status="scheduled"
        )