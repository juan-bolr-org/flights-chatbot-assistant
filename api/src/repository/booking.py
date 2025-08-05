from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
import datetime
from fastapi import Depends
from resources.database import get_database_session
from models import Booking, Flight


class BookingRepository(ABC):
    """Abstract base class for Booking repository operations."""
    
    @abstractmethod
    def create(self, user_id: int, flight_id: int, status: str = "booked") -> Booking:
        """Create a new booking."""
        pass
    
    @abstractmethod
    def find_by_id(self, booking_id: int) -> Optional[Booking]:
        """Find a booking by ID."""
        pass
    
    @abstractmethod
    def find_existing_booking(self, user_id: int, flight_id: int) -> Optional[Booking]:
        """Find existing active booking for user and flight."""
        pass
    
    @abstractmethod
    def update_status(self, booking_id: int, status: str, cancelled_at: Optional[datetime.datetime] = None) -> Booking:
        """Update booking status and cancelled_at timestamp."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: int, status_filter: Optional[str] = None) -> List[Booking]:
        """Find all bookings for a user with optional status filter."""
        pass
    
    @abstractmethod
    def delete_by_id(self, booking_id: int) -> bool:
        """Delete a booking by ID. Returns True if deleted, False if not found."""
        pass


class BookingSqliteRepository(BookingRepository):
    """SQLite implementation of BookingRepository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, flight_id: int, status: str = "booked") -> Booking:
        """Create a new booking."""
        booking = Booking(
            user_id=user_id,
            flight_id=flight_id,
            status=status
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
    
    def find_by_id(self, booking_id: int) -> Optional[Booking]:
        """Find a booking by ID."""
        return self.db.query(Booking).filter(Booking.id == booking_id).first()
    
    def find_existing_booking(self, user_id: int, flight_id: int) -> Optional[Booking]:
        """Find existing active booking for user and flight."""
        return self.db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.flight_id == flight_id,
            Booking.status == "booked"
        ).first()
    
    def update_status(self, booking_id: int, status: str, cancelled_at: Optional[datetime.datetime] = None) -> Booking:
        """Update booking status and cancelled_at timestamp."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking with ID {booking_id} not found")
        
        booking.status = status
        if cancelled_at:
            booking.cancelled_at = cancelled_at
        
        self.db.commit()
        self.db.refresh(booking)
        return booking
    
    def find_by_user_id(self, user_id: int, status_filter: Optional[str] = None) -> List[Booking]:
        """Find all bookings for a user with optional status filter."""
        query = self.db.query(Booking).filter(Booking.user_id == user_id)
        
        if status_filter:
            if status_filter == "upcoming":
                # Show booked flights that haven't departed yet
                query = query.join(Flight).filter(
                    Booking.status == "booked",
                    Flight.departure_time > datetime.datetime.now(datetime.UTC)
                )
            elif status_filter == "past":
                # Show flights that have departed or been cancelled
                query = query.join(Flight).filter(
                    or_(
                        Flight.departure_time <= datetime.datetime.now(datetime.UTC),
                        Booking.status == "cancelled"
                    )
                )
            else:
                query = query.filter(Booking.status == status_filter)
        
        return query.order_by(Booking.booked_at.desc()).all()
    
    def delete_by_id(self, booking_id: int) -> bool:
        """Delete a booking by ID. Returns True if deleted, False if not found."""
        booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return False
        
        self.db.delete(booking)
        self.db.commit()
        return True


def create_booking_repository(db: Session = Depends(get_database_session)) -> BookingRepository:
    """Dependency injection function to create BookingRepository instance."""
    return BookingSqliteRepository(db)
