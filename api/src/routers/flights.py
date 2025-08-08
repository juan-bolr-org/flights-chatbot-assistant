from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from repository import User
from schemas import FlightResponse, FlightCreate, PaginatedResponse
from resources.dependencies import get_current_user
from resources.logging import get_logger
from services import FlightService, create_flight_service
from exceptions import ApiException
from utils.error_handlers import api_exception_to_http_exception

router = APIRouter(prefix="/flights", tags=["flights"])
logger = get_logger("flights_router")

@router.get("/search", response_model=PaginatedResponse[FlightResponse])
def search_flights(
    origin: Optional[str] = Query(None, description="Origin airport code or city name"),
    destination: Optional[str] = Query(None, description="Destination airport code or city name"), 
    departure_date: Optional[str] = Query(None, description="Departure date in YYYY-MM-DD format"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    flight_service: FlightService = Depends(create_flight_service)
):
    try:
        flights = flight_service.search_flights(origin, destination, departure_date, page, size)
        return flights
        
    except ApiException as e:
        logger.warning(f"Invalid parameters provided - origin: {origin}, destination: {destination}, departure_date: {departure_date}")
        raise api_exception_to_http_exception(e)
    except Exception as e:
        logger.error(f"Error searching flights with filters - origin: {origin}, destination: {destination}, departure_date: {departure_date}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error searching flights: {str(e)}"
        )

@router.post("", response_model=FlightResponse)
def create_flight(
    flight: FlightCreate,
    current_user: User = Depends(get_current_user),
    flight_service: FlightService = Depends(create_flight_service)
):
    try:
        new_flight = flight_service.create_flight(current_user, flight)
        return new_flight
        
    except Exception as e:
        logger.error(f"Error creating flight by user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error creating flight: {str(e)}"
        )

@router.get("/list", response_model=PaginatedResponse[FlightResponse])
def list_flights(
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    flight_service: FlightService = Depends(create_flight_service)
):
    try:
        flights = flight_service.list_flights(page, size)
        return flights
        
    except Exception as e:
        logger.error(f"Error retrieving flights list (page: {page}, size: {size}): {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving flights: {str(e)}"
        )
