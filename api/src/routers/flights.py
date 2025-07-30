from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import datetime
from datetime import timedelta
from schemas import FlightResponse, FlightCreate
from models import User, Flight
from utils import get_db, get_current_user

router = APIRouter(prefix="/flights", tags=["flights"])

@router.get("/search", response_model=List[FlightResponse])
def search_flights(
    origin: str, 
    destination: str, 
    departure_date: str,
    db: Session = Depends(get_db)
):
    # Parse the departure date
    try:
        date_obj = datetime.datetime.strptime(departure_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    # Search flights for the given criteria
    flights = db.query(Flight).filter(
        Flight.origin.ilike(f"%{origin}%"),
        Flight.destination.ilike(f"%{destination}%"),
        Flight.departure_time >= date_obj,
        Flight.departure_time < date_obj + timedelta(days=1),
        Flight.status == "scheduled"
    ).all()
    
    return flights

@router.post("", response_model=FlightResponse)
def create_flight(
    flight: FlightCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    return new_flight

@router.get("/list", response_model=List[FlightResponse])
def list_flights(
    db: Session = Depends(get_db)
):
    flights = db.query(Flight).all()
    return flights
