from fastapi import APIRouter, Depends, HTTPException
from typing import List
from repository.user import User
from schemas import FlightResponse, FlightCreate
from resources.dependencies import get_current_user
from resources.logging import get_logger
from repository import FlightRepository, create_flight_repository

router = APIRouter(prefix="/flights", tags=["flights"])
logger = get_logger("flights_router")

@router.get("/search", response_model=List[FlightResponse])
def search_flights(
    origin: str, 
    destination: str, 
    departure_date: str,
    flight_repo: FlightRepository = Depends(create_flight_repository)
):
    try:
        logger.debug(f"Searching flights from {origin} to {destination} on {departure_date}")
        
        flights = flight_repo.search_flights(origin, destination, departure_date)
        
        logger.info(f"Found {len(flights)} flights from {origin} to {destination} on {departure_date}")
        logger.debug(f"Flight IDs found: {[flight.id for flight in flights]}")
        
        return flights
        
    except ValueError as e:
        logger.warning(f"Invalid date format provided: {departure_date}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching flights from {origin} to {destination}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error searching flights: {str(e)}"
        )

@router.post("", response_model=FlightResponse)
def create_flight(
    flight: FlightCreate,
    current_user: User = Depends(get_current_user),
    flight_repo: FlightRepository = Depends(create_flight_repository)
):
    try:
        logger.debug(f"Creating flight from {flight.origin} to {flight.destination} by user {current_user.id}")
        
        # Optionally, check if current_user is admin here
        new_flight = flight_repo.create(
            origin=flight.origin,
            destination=flight.destination,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            airline=flight.airline,
            price=int(flight.price),
            status=flight.status or "scheduled"
        )
        
        logger.info(f"Successfully created flight {new_flight.id} from {flight.origin} to {flight.destination} by user {current_user.email}")
        return new_flight
        
    except Exception as e:
        logger.error(f"Error creating flight by user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error creating flight: {str(e)}"
        )

@router.get("/list", response_model=List[FlightResponse])
def list_flights(
    flight_repo: FlightRepository = Depends(create_flight_repository)
):
    try:
        logger.debug("Retrieving all flights")
        
        flights = flight_repo.list_all()
        
        logger.info(f"Successfully retrieved {len(flights)} flights")
        logger.debug(f"Flight IDs retrieved: {[flight.id for flight in flights]}")
        
        return flights
        
    except Exception as e:
        logger.error(f"Error retrieving flights list: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving flights: {str(e)}"
        )
