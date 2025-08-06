"""
Tests for FlightRepository - Repository Layer
Tests use in-memory SQLite database to ensure data isolation.
"""
import pytest
import os
import sys
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Base, Flight
from repository.flight import FlightSqliteRepository


class TestFlightRepository:
    """Test suite for FlightRepository using in-memory SQLite database."""
    
    @pytest.fixture
    def db_session(self):
        """Create an in-memory SQLite database session."""
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @pytest.fixture
    def flight_repo(self, db_session):
        """Create FlightRepository instance with test database session."""
        return FlightSqliteRepository(db_session)
    
    @pytest.fixture
    def sample_flight_data(self):
        """Sample flight data for testing."""
        return {
            "origin": "New York",
            "destination": "Los Angeles",
            "departure_time": datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc),
            "arrival_time": datetime(2025, 12, 25, 13, 30, 0, tzinfo=timezone.utc),
            "airline": "American Airlines",
            "price": 299,
            "status": "scheduled"
        }
    
    @pytest.fixture
    def sample_flight_data_2(self):
        """Second sample flight data for testing."""
        return {
            "origin": "Chicago",
            "destination": "Miami",
            "departure_time": datetime(2025, 12, 26, 14, 0, 0, tzinfo=timezone.utc),
            "arrival_time": datetime(2025, 12, 26, 17, 45, 0, tzinfo=timezone.utc),
            "airline": "Delta Airlines",
            "price": 399,
            "status": "scheduled"
        }
    
    # ===== POSITIVE TESTS =====
    
    def test_create_flight_success(self, flight_repo, sample_flight_data):
        """Test successful flight creation."""
        flight = flight_repo.create(**sample_flight_data)
        
        assert flight.id is not None
        assert flight.origin == sample_flight_data["origin"]
        assert flight.destination == sample_flight_data["destination"]
        
        # Handle timezone differences - if stored datetime is naive, assume UTC
        expected_departure = sample_flight_data["departure_time"]
        actual_departure = flight.departure_time
        if actual_departure.tzinfo is None:
            actual_departure = actual_departure.replace(tzinfo=timezone.utc)
        assert actual_departure == expected_departure
        
        expected_arrival = sample_flight_data["arrival_time"]
        actual_arrival = flight.arrival_time
        if actual_arrival.tzinfo is None:
            actual_arrival = actual_arrival.replace(tzinfo=timezone.utc)
        assert actual_arrival == expected_arrival
        
        assert flight.airline == sample_flight_data["airline"]
        assert flight.price == sample_flight_data["price"]
        assert flight.status == sample_flight_data["status"]
    
    def test_create_flight_default_status(self, flight_repo, sample_flight_data):
        """Test flight creation with default status."""
        del sample_flight_data["status"]
        flight = flight_repo.create(**sample_flight_data)
        
        assert flight.id is not None
        assert flight.status == "scheduled"
        assert flight.origin == sample_flight_data["origin"]
    
    def test_find_by_id_success(self, flight_repo, sample_flight_data):
        """Test finding flight by ID when flight exists."""
        created_flight = flight_repo.create(**sample_flight_data)
        found_flight = flight_repo.find_by_id(created_flight.id)
        
        assert found_flight is not None
        assert found_flight.id == created_flight.id
        assert found_flight.origin == sample_flight_data["origin"]
        assert found_flight.destination == sample_flight_data["destination"]
    
    def test_list_all_success(self, flight_repo, sample_flight_data, sample_flight_data_2):
        """Test listing all flights."""
        flight1 = flight_repo.create(**sample_flight_data)
        flight2 = flight_repo.create(**sample_flight_data_2)
        
        all_flights, total = flight_repo.list_all()
        
        assert len(all_flights) == 2
        assert total == 2
        flight_ids = [f.id for f in all_flights]
        assert flight1.id in flight_ids
        assert flight2.id in flight_ids
    
    def test_search_flights_by_date_success(self, flight_repo, sample_flight_data):
        """Test searching flights by origin, destination, and date."""
        flight_repo.create(**sample_flight_data)
        
        # Search for the flight using date string
        flights, total = flight_repo.search_flights("New York", "Los Angeles", "2025-12-25")
        
        assert len(flights) == 1
        assert total == 1
        assert flights[0].origin == "New York"
        assert flights[0].destination == "Los Angeles"
        assert flights[0].status == "scheduled"
    
    def test_search_flights_case_insensitive(self, flight_repo, sample_flight_data):
        """Test searching flights with case insensitive matching."""
        flight_repo.create(**sample_flight_data)
        
        # Search with different case
        flights, total = flight_repo.search_flights("new york", "los angeles", "2025-12-25")
        
        assert len(flights) == 1
        assert total == 1
        assert flights[0].origin == "New York"
        assert flights[0].destination == "Los Angeles"
    
    def test_search_flights_partial_match(self, flight_repo, sample_flight_data):
        """Test searching flights with partial city name matching."""
        flight_repo.create(**sample_flight_data)
        
        # Search with partial names
        flights, total = flight_repo.search_flights("York", "Angeles", "2025-12-25")
        
        assert len(flights) == 1
        assert total == 1
        assert flights[0].origin == "New York"
        assert flights[0].destination == "Los Angeles"
    
    def test_search_flights_filters_by_status(self, flight_repo, sample_flight_data):
        """Test that search only returns scheduled flights."""
        # Create scheduled flight
        scheduled_flight = flight_repo.create(**sample_flight_data)
        
        # Create cancelled flight
        sample_flight_data["status"] = "cancelled"
        sample_flight_data["departure_time"] = datetime(2025, 12, 25, 15, 0, 0, tzinfo=timezone.utc)
        flight_repo.create(**sample_flight_data)
        
        # Search should only return scheduled flight
        flights, total = flight_repo.search_flights("New York", "Los Angeles", "2025-12-25")
        
        assert len(flights) == 1
        assert total == 1
        assert flights[0].id == scheduled_flight.id
        assert flights[0].status == "scheduled"
    
    def test_find_available_by_id_success(self, flight_repo, sample_flight_data):
        """Test finding available (scheduled) flight by ID."""
        created_flight = flight_repo.create(**sample_flight_data)
        found_flight = flight_repo.find_available_by_id(created_flight.id)
        
        assert found_flight is not None
        assert found_flight.id == created_flight.id
        assert found_flight.status == "scheduled"
    
    def test_search_flights_date_range(self, flight_repo, sample_flight_data, sample_flight_data_2):
        """Test that search includes all flights within the specified date."""
        # Create flights at different times on same date
        sample_flight_data["departure_time"] = datetime(2025, 12, 25, 8, 0, 0, tzinfo=timezone.utc)
        flight1 = flight_repo.create(**sample_flight_data)
        
        sample_flight_data_2["origin"] = "New York"
        sample_flight_data_2["destination"] = "Los Angeles"
        sample_flight_data_2["departure_time"] = datetime(2025, 12, 25, 20, 0, 0, tzinfo=timezone.utc)
        flight2 = flight_repo.create(**sample_flight_data_2)
        
        flights, total = flight_repo.search_flights("New York", "Los Angeles", "2025-12-25")
        
        assert len(flights) == 2
        assert total == 2
        flight_ids = [f.id for f in flights]
        assert flight1.id in flight_ids
        assert flight2.id in flight_ids
    
    # ===== NEGATIVE TESTS =====
    
    def test_find_by_id_not_found(self, flight_repo):
        """Test finding flight by ID when flight doesn't exist."""
        found_flight = flight_repo.find_by_id(999)
        assert found_flight is None
    
    def test_search_flights_no_matches(self, flight_repo, sample_flight_data):
        """Test searching flights when no matches exist."""
        flight_repo.create(**sample_flight_data)
        
        # Search for different route
        flights, total = flight_repo.search_flights("Boston", "Seattle", "2025-12-25")
        assert len(flights) == 0
        assert total == 0
    
    def test_search_flights_different_date(self, flight_repo, sample_flight_data):
        """Test searching flights on different date."""
        flight_repo.create(**sample_flight_data)
        
        # Search for different date
        flights, total = flight_repo.search_flights("New York", "Los Angeles", "2025-12-26")
        assert len(flights) == 0
        assert total == 0
    
    def test_search_flights_invalid_date_format(self, flight_repo):
        """Test searching flights with invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format. Use YYYY-MM-DD"):
            flight_repo.search_flights("New York", "Los Angeles", "2025/12/25")
    
    def test_search_flights_invalid_date_format_2(self, flight_repo):
        """Test searching flights with another invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format. Use YYYY-MM-DD"):
            flight_repo.search_flights("New York", "Los Angeles", "25-12-2025")
    
    def test_find_available_by_id_cancelled_flight(self, flight_repo, sample_flight_data):
        """Test finding available flight when flight is cancelled."""
        sample_flight_data["status"] = "cancelled"
        created_flight = flight_repo.create(**sample_flight_data)
        
        found_flight = flight_repo.find_available_by_id(created_flight.id)
        assert found_flight is None
    
    def test_find_available_by_id_not_found(self, flight_repo):
        """Test finding available flight when flight doesn't exist."""
        found_flight = flight_repo.find_available_by_id(999)
        assert found_flight is None
    
    def test_list_all_empty(self, flight_repo):
        """Test listing flights when no flights exist."""
        all_flights, total = flight_repo.list_all()
        assert len(all_flights) == 0
        assert total == 0
    
    # ===== EDGE CASES =====
    
    def test_create_multiple_flights_same_route(self, flight_repo, sample_flight_data):
        """Test creating multiple flights on same route."""
        flight1 = flight_repo.create(**sample_flight_data)
        
        # Create second flight with different time
        new_departure = datetime(2025, 12, 25, 15, 0, 0, tzinfo=timezone.utc)
        new_arrival = datetime(2025, 12, 25, 18, 30, 0, tzinfo=timezone.utc)
        sample_flight_data["departure_time"] = new_departure
        sample_flight_data["arrival_time"] = new_arrival
        flight2 = flight_repo.create(**sample_flight_data)
        
        assert flight1.id != flight2.id
        assert flight1.origin == flight2.origin
        assert flight1.destination == flight2.destination
        
        # Handle timezone differences for comparison
        flight1_departure = flight1.departure_time
        if flight1_departure.tzinfo is None:
            flight1_departure = flight1_departure.replace(tzinfo=timezone.utc)
            
        flight2_departure = flight2.departure_time
        if flight2_departure.tzinfo is None:
            flight2_departure = flight2_departure.replace(tzinfo=timezone.utc)
            
        assert flight1_departure != flight2_departure
    
    def test_search_flights_boundary_date(self, flight_repo, sample_flight_data):
        """Test searching flights at date boundary (end of day)."""
        # Create flight just before midnight
        sample_flight_data["departure_time"] = datetime(2025, 12, 25, 23, 59, 59, tzinfo=timezone.utc)
        flight = flight_repo.create(**sample_flight_data)
        
        flights, total = flight_repo.search_flights("New York", "Los Angeles", "2025-12-25")
        
        assert len(flights) == 1
        assert total == 1
        assert flights[0].id == flight.id
    
    def test_search_flights_next_day_exclusion(self, flight_repo, sample_flight_data):
        """Test that search excludes flights from next day."""
        # Create flight just after midnight of next day
        sample_flight_data["departure_time"] = datetime(2025, 12, 26, 0, 0, 1, tzinfo=timezone.utc)
        flight_repo.create(**sample_flight_data)
        
        # Should not find flight when searching previous day
        flights, total = flight_repo.search_flights("New York", "Los Angeles", "2025-12-25")
        assert len(flights) == 0
        assert total == 0
    
    def test_create_flight_with_same_departure_arrival_time(self, flight_repo, sample_flight_data):
        """Test creating flight with same departure and arrival time."""
        same_time = datetime(2025, 12, 25, 10, 0, 0, tzinfo=timezone.utc)
        sample_flight_data["departure_time"] = same_time
        sample_flight_data["arrival_time"] = same_time
        
        flight = flight_repo.create(**sample_flight_data)
        
        assert flight.id is not None
        
        # Handle timezone differences - if stored datetime is naive, assume UTC
        actual_departure = flight.departure_time
        if actual_departure.tzinfo is None:
            actual_departure = actual_departure.replace(tzinfo=timezone.utc)
        
        actual_arrival = flight.arrival_time
        if actual_arrival.tzinfo is None:
            actual_arrival = actual_arrival.replace(tzinfo=timezone.utc)
            
        assert actual_departure == actual_arrival
    
    def test_search_flights_empty_strings(self, flight_repo, sample_flight_data):
        """Test searching flights with empty origin/destination."""
        flight_repo.create(**sample_flight_data)
        
        # Empty strings should match any flight (due to LIKE %%)
        flights, total = flight_repo.search_flights("", "", "2025-12-25")
        assert len(flights) == 1
        assert total == 1
    
    def test_price_precision(self, flight_repo, sample_flight_data):
        """Test that price is stored as integer correctly."""
        sample_flight_data["price"] = 29999  # High price
        flight = flight_repo.create(**sample_flight_data)
        
        found_flight = flight_repo.find_by_id(flight.id)
        assert found_flight.price == 29999
        assert isinstance(found_flight.price, int)
