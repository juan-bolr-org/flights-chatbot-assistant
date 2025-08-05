from abc import ABC, abstractmethod
from typing import List
from fastapi import Depends
from repository import User, Flight
from schemas import FlightCreate
from repository import FlightRepository, create_flight_repository
from resources.logging import get_logger
from exceptions import InvalidDateFormatError, InvalidFlightTimesError, InvalidFlightPriceError

logger = get_logger("flight_service")


class FlightService(ABC):
    """Abstract base class for Flight service operations."""
    
    @abstractmethod
    def search_flights(self, origin: str, destination: str, departure_date: str) -> List[Flight]:
        """Search for flights by origin, destination, and departure date."""
        pass
    
    @abstractmethod
    def create_flight(self, user: User, flight: FlightCreate) -> Flight:
        """Create a new flight."""
        pass
    
    @abstractmethod
    def list_flights(self) -> List[Flight]:
        """Get all flights."""
        pass


class FlightBusinessService(FlightService):
    """Implementation of FlightService with business logic."""
    
    def __init__(self, flight_repo: FlightRepository):
        self.flight_repo = flight_repo
    
    def search_flights(self, origin: str, destination: str, departure_date: str) -> List[Flight]:
        """Search for flights by origin, destination, and departure date."""
        logger.debug(f"Searching flights from {origin} to {destination} on {departure_date}")
        
        try:
            flights = self.flight_repo.search_flights(origin, destination, departure_date)
            
            logger.info(f"Found {len(flights)} flights from {origin} to {destination} on {departure_date}")
            logger.debug(f"Flight IDs found: {[flight.id for flight in flights]}")
            
            return flights
        except ValueError as e:
            logger.warning(f"Invalid date format provided: {departure_date}")
            raise InvalidDateFormatError(departure_date)
    
    def create_flight(self, user: User, flight: FlightCreate) -> Flight:
        """Create a new flight."""
        logger.debug(f"Creating flight from {flight.origin} to {flight.destination} by user {user.id}")

        if flight.departure_time >= flight.arrival_time:
            logger.error(f"Invalid flight times: departure {flight.departure_time} must be before arrival {flight.arrival_time}")
            raise InvalidFlightTimesError(str(flight.departure_time), str(flight.arrival_time))
        if flight.price <= 0:
            logger.error(f"Invalid flight price: {flight.price} must be greater than 0")
            raise InvalidFlightPriceError(flight.price)

        
        # Optionally, check if current_user is admin here
        new_flight = self.flight_repo.create(
            origin=flight.origin,
            destination=flight.destination,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            airline=flight.airline,
            price=int(flight.price),
            status=flight.status or "scheduled"
        )
        
        logger.info(f"Successfully created flight {new_flight.id} from {flight.origin} to {flight.destination} by user {user.email}")
        return new_flight
    
    def list_flights(self) -> List[Flight]:
        """Get all flights."""
        logger.debug("Retrieving all flights")
        
        flights = self.flight_repo.list_all()
        
        logger.info(f"Successfully retrieved {len(flights)} flights")
        logger.debug(f"Flight IDs retrieved: {[flight.id for flight in flights]}")
        
        return flights


def create_flight_service(
    flight_repo: FlightRepository = Depends(create_flight_repository)
) -> FlightService:
    """Dependency injection function to create FlightService instance."""
    return FlightBusinessService(flight_repo)
