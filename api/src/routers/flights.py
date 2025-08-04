from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
from datetime import timedelta
from schemas import FlightResponse, FlightCreate
from models import User, Flight
from resources.dependencies import get_database_session as get_db, get_current_user
from resources.logging import get_logger

router = APIRouter(prefix="/flights", tags=["flights"])
logger = get_logger("flights_router")

@router.get("/search", response_model=List[FlightResponse])
def search_flights(
    origin: str, 
    destination: str, 
    departure_date: str,
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Searching flights from {origin} to {destination} on {departure_date}")
        
        # Parse the departure date
        try:
            date_obj = datetime.datetime.strptime(departure_date, "%Y-%m-%d").date()
        except ValueError:
            logger.warning(f"Invalid date format provided: {departure_date}")
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Search flights for the given criteria
        flights = db.query(Flight).filter(
            Flight.origin.ilike(f"%{origin}%"),
            Flight.destination.ilike(f"%{destination}%"),
            Flight.departure_time >= date_obj,
            Flight.departure_time < date_obj + timedelta(days=1),
            Flight.status == "scheduled"
        ).all()
        
        logger.info(f"Found {len(flights)} flights from {origin} to {destination} on {departure_date}")
        logger.debug(f"Flight IDs found: {[flight.id for flight in flights]}")
        
        return flights
        
    except HTTPException:
        raise
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
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Creating flight from {flight.origin} to {flight.destination} by user {current_user.id}")
        
        # Optionally, check if current_user is admin here
        new_flight = Flight(
            origin=flight.origin,
            destination=flight.destination,
            departure_time=flight.departure_time,
            arrival_time=flight.arrival_time,
            airline=flight.airline,
            status=flight.status or "scheduled"
        )
        db.add(new_flight)
        db.commit()
        db.refresh(new_flight)
        
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
    db: Session = Depends(get_db)
):
    try:
        logger.debug("Retrieving all flights")
        
        flights = db.query(Flight).all()
        
        logger.info(f"Successfully retrieved {len(flights)} flights")
        logger.debug(f"Flight IDs retrieved: {[flight.id for flight in flights]}")
        
        return flights
        
    except Exception as e:
        logger.error(f"Error retrieving flights list: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving flights: {str(e)}"
        )
