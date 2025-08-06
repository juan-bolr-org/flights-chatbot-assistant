from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
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
    def find_by_user_id_paginated(self, user_id: int, status_filter: Optional[str] = None, 
                                 booked_date: Optional[str] = None, departure_date: Optional[str] = None, 
                                 page: int = 1, size: int = 10) -> Tuple[List[Booking], int]:
        """Find all bookings for a user with optional filters and pagination. Returns (bookings, total_count)."""
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
                # Compare with naive datetime since database stores naive datetimes
                query = query.join(Flight).filter(
                    Booking.status == "booked",
                    Flight.departure_time > datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                )
            elif status_filter == "past":
                # Show flights that have departed or been cancelled
                # Compare with naive datetime since database stores naive datetimes
                query = query.join(Flight).filter(
                    or_(
                        Flight.departure_time <= datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
                        Booking.status == "cancelled"
                    )
                )
            else:
                query = query.filter(Booking.status == status_filter)
        
        return query.order_by(Booking.booked_at.desc()).all()
    
    def find_by_user_id_paginated(self, user_id: int, status_filter: Optional[str] = None, 
                                 booked_date: Optional[str] = None, departure_date: Optional[str] = None, 
                                 page: int = 1, size: int = 10) -> Tuple[List[Booking], int]:
        """Find all bookings for a user with optional filters and pagination. Returns (bookings, total_count)."""
        query = self.db.query(Booking).join(Flight).filter(Booking.user_id == user_id)
        
        # Apply status filter
        if status_filter:
            now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            if status_filter == "booked":
                # Show active bookings for upcoming flights
                query = query.filter(
                    and_(
                        Booking.status == "booked",
                        Flight.departure_time > now
                    )
                )
            elif status_filter == "completed":
                # Show booked flights that have already departed
                query = query.filter(
                    and_(
                        Booking.status == "booked",
                        Flight.departure_time <= now
                    )
                )
            elif status_filter == "cancelled":
                # Show cancelled bookings
                query = query.filter(Booking.status == "cancelled")
        
        # Apply booking date filter
        if booked_date:
            try:
                # Parse the date string (expected format: YYYY-MM-DD)
                filter_date = datetime.datetime.strptime(booked_date, "%Y-%m-%d").date()
                # Filter by the date part of booked_at
                query = query.filter(func.date(Booking.booked_at) == filter_date)
            except ValueError:
                # If date parsing fails, ignore the filter
                pass
        
        # Apply departure date filter
        if departure_date:
            try:
                # Parse the date string (expected format: YYYY-MM-DD)
                filter_date = datetime.datetime.strptime(departure_date, "%Y-%m-%d").date()
                # Filter by the date part of flight departure_time
                query = query.filter(func.date(Flight.departure_time) == filter_date)
            except ValueError:
                # If date parsing fails, ignore the filter
                pass
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * size
        bookings = query.order_by(Booking.booked_at.desc()).offset(offset).limit(size).all()
        
        return bookings, total
    
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
