from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import Depends
from resources.database import get_database_session
from models import Flight


class FlightRepository(ABC):
    """Abstract base class for Flight repository operations."""
    
    @abstractmethod
    def create(self, origin: str, destination: str, departure_time: datetime, 
               arrival_time: datetime, airline: str, price: int, status: str = "scheduled") -> Flight:
        """Create a new flight."""
        pass
    
    @abstractmethod
    def find_by_id(self, flight_id: int) -> Optional[Flight]:
        """Find a flight by ID."""
        pass
    
    @abstractmethod
    def search_flights(self, origin: Optional[str] = None, destination: Optional[str] = None, 
                      departure_date: Optional[str] = None, page: int = 1, size: int = 10) -> tuple[List[Flight], int]:
        """Search for flights by origin, destination, and departure date with pagination."""
        pass
    
    @abstractmethod
    def list_all(self, page: int = 1, size: int = 10) -> tuple[List[Flight], int]:
        """Get all flights with pagination."""
        pass
    
    @abstractmethod
    def find_available_by_id(self, flight_id: int) -> Optional[Flight]:
        """Find an available (scheduled) flight by ID."""
        pass


class FlightSqliteRepository(FlightRepository):
    """SQLite implementation of FlightRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, origin: str, destination: str, departure_time: datetime, 
               arrival_time: datetime, airline: str, price: int, status: str = "scheduled") -> Flight:
        """Create a new flight."""
        flight = Flight(
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            airline=airline,
            price=price,
            status=status
        )
        self.db.add(flight)
        self.db.commit()
        self.db.refresh(flight)
        return flight
    
    def find_by_id(self, flight_id: int) -> Optional[Flight]:
        """Find a flight by ID."""
        return self.db.query(Flight).filter(Flight.id == flight_id).first()
    
    def search_flights(self, origin: Optional[str] = None, destination: Optional[str] = None, 
                      departure_date: Optional[str] = None, page: int = 1, size: int = 10) -> tuple[List[Flight], int]:
        """Search for flights by origin, destination, and departure date with pagination."""
        query = self.db.query(Flight).filter(Flight.status == "scheduled")
        
        # Apply filters only if parameters are provided
        if origin:
            query = query.filter(Flight.origin.ilike(f"%{origin}%"))
        
        if destination:
            query = query.filter(Flight.destination.ilike(f"%{destination}%"))
        
        if departure_date:
            try:
                date_obj = datetime.strptime(departure_date, "%Y-%m-%d").date()
                query = query.filter(
                    Flight.departure_time >= date_obj,
                    Flight.departure_time < date_obj + timedelta(days=1)
                )
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        # Get total count before applying pagination
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        flights = query.offset(offset).limit(size).all()
        
        return flights, total
    
    def list_all(self, page: int = 1, size: int = 10) -> tuple[List[Flight], int]:
        """Get all flights with pagination."""
        query = self.db.query(Flight)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        flights = query.offset(offset).limit(size).all()
        
        return flights, total
    
    def find_available_by_id(self, flight_id: int) -> Optional[Flight]:
        """Find an available (scheduled) flight by ID."""
        return self.db.query(Flight).filter(
            Flight.id == flight_id, 
            Flight.status == "scheduled"
        ).first()


def create_flight_repository(db: Session = Depends(get_database_session)) -> FlightRepository:
    """Dependency injection function to create FlightRepository instance."""
    return FlightSqliteRepository(db)
