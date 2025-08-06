from abc import ABC, abstractmethod
from typing import List, Optional
from fastapi import Depends
from repository import User, Flight
from schemas import FlightCreate, FlightResponse, PaginatedResponse
from repository import FlightRepository, create_flight_repository
from resources.logging import get_logger
from exceptions import InvalidDateFormatError, InvalidFlightTimesError, InvalidFlightPriceError
import math

logger = get_logger("flight_service")


class FlightService(ABC):
    """Abstract base class for Flight service operations."""
    
    @abstractmethod
    def search_flights(self, origin: Optional[str] = None, destination: Optional[str] = None, 
                      departure_date: Optional[str] = None, page: int = 1, size: int = 10) -> PaginatedResponse[FlightResponse]:
        """Search for flights by origin, destination, and departure date with pagination."""
        pass
    
    @abstractmethod
    def create_flight(self, user: User, flight: FlightCreate) -> FlightResponse:
        """Create a new flight."""
        pass
    
    @abstractmethod
    def list_flights(self, page: int = 1, size: int = 10) -> PaginatedResponse[FlightResponse]:
        """Get all flights with pagination."""
        pass


class FlightBusinessService(FlightService):
    """Implementation of FlightService with business logic."""
    
    def __init__(self, flight_repo: FlightRepository):
        self.flight_repo = flight_repo
    
    def search_flights(self, origin: Optional[str] = None, destination: Optional[str] = None, 
                      departure_date: Optional[str] = None, page: int = 1, size: int = 10) -> PaginatedResponse[FlightResponse]:
        """Search for flights by origin, destination, and departure date with pagination."""
        # Log the search parameters
        search_params = []
        if origin:
            search_params.append(f"origin: {origin}")
        if destination:
            search_params.append(f"destination: {destination}")
        if departure_date:
            search_params.append(f"departure_date: {departure_date}")
        
        logger.debug(f"Searching flights with filters: {', '.join(search_params) or 'no filters'}, page: {page}, size: {size}")
        
        try:
            flights, total = self.flight_repo.search_flights(origin, destination, departure_date, page, size)
            
            logger.info(f"Found {len(flights)} flights (total: {total}) with filters: {', '.join(search_params) or 'no filters'}")
            logger.debug(f"Flight IDs found: {[flight.id for flight in flights]}")
            
            # Convert Flight models to FlightResponse schemas
            flight_responses = [
                FlightResponse(
                    id=flight.id,
                    origin=flight.origin,
                    destination=flight.destination,
                    departure_time=flight.departure_time,
                    arrival_time=flight.arrival_time,
                    airline=flight.airline,
                    status=flight.status,
                    price=flight.price
                ) for flight in flights
            ]
            
            # Calculate total pages
            pages = math.ceil(total / size) if total > 0 else 1
            
            return PaginatedResponse(
                items=flight_responses,
                total=total,
                page=page,
                size=size,
                pages=pages
            )
        except ValueError as e:
            logger.warning(f"Invalid date format provided: {departure_date}")
            raise InvalidDateFormatError(departure_date)
    
    def create_flight(self, user: User, flight: FlightCreate) -> FlightResponse:
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
        
        # Convert Flight model to FlightResponse schema
        return FlightResponse(
            id=new_flight.id,
            origin=new_flight.origin,
            destination=new_flight.destination,
            departure_time=new_flight.departure_time,
            arrival_time=new_flight.arrival_time,
            airline=new_flight.airline,
            status=new_flight.status,
            price=new_flight.price
        )
    
    def list_flights(self, page: int = 1, size: int = 10) -> PaginatedResponse[FlightResponse]:
        """Get all flights with pagination."""
        logger.debug(f"Retrieving all flights, page: {page}, size: {size}")
        
        flights, total = self.flight_repo.list_all(page, size)
        
        logger.info(f"Successfully retrieved {len(flights)} flights (total: {total})")
        logger.debug(f"Flight IDs retrieved: {[flight.id for flight in flights]}")
        
        # Convert Flight models to FlightResponse schemas
        flight_responses = [
            FlightResponse(
                id=flight.id,
                origin=flight.origin,
                destination=flight.destination,
                departure_time=flight.departure_time,
                arrival_time=flight.arrival_time,
                airline=flight.airline,
                status=flight.status,
                price=int(flight.price)
            ) for flight in flights
        ]
        
        # Calculate total pages
        pages = math.ceil(total / size) if total > 0 else 1
        
        return PaginatedResponse(
            items=flight_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


def create_flight_service(
    flight_repo: FlightRepository = Depends(create_flight_repository)
) -> FlightService:
    """Dependency injection function to create FlightService instance."""
    return FlightBusinessService(flight_repo)
