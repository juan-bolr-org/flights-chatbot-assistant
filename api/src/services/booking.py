from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from fastapi import Depends
from repository import User, Booking
from schemas import BookingCreate, BookingUpdate
from repository import BookingRepository, FlightRepository, create_booking_repository, create_flight_repository
from resources.logging import get_logger
from exceptions import (
    FlightNotAvailableError, 
    BookingAlreadyExistsError, 
    BookingNotFoundError,
    AccessDeniedError,
    BookingCannotBeCancelledError,
    PastFlightCannotBeCancelledError
)
import datetime

logger = get_logger("booking_service")


class BookingService(ABC):
    """Abstract base class for Booking service operations."""
    
    @abstractmethod
    def create_booking(self, user: User, booking: BookingCreate) -> Booking:
        """Create a new booking for a user."""
        pass
    
    @abstractmethod
    def update_booking(self, user: User, booking_id: int, booking_update: BookingUpdate) -> Booking:
        """Update a booking for a user."""
        pass
    
    @abstractmethod
    def delete_booking(self, user: User, booking_id: int) -> Dict[str, str]:
        """Delete/cancel a booking for a user."""
        pass
    
    @abstractmethod
    def get_user_bookings(self, user: User, status: Optional[str] = None) -> List[Booking]:
        """Get all bookings for a user with optional status filter."""
        pass


class BookingBusinessService(BookingService):
    """Implementation of BookingService with business logic."""
    
    def __init__(self, booking_repo: BookingRepository, flight_repo: FlightRepository):
        self.booking_repo = booking_repo
        self.flight_repo = flight_repo
    
    def create_booking(self, user: User, booking: BookingCreate) -> Booking:
        """Create a new booking for a user."""
        logger.debug(f"Creating booking for user {user.id}, flight {booking.flight_id}")
        
        # Check if flight exists and is available
        flight = self.flight_repo.find_available_by_id(booking.flight_id)
        if not flight:
            logger.warning(f"Flight {booking.flight_id} not found or not available for user {user.email}")
            raise FlightNotAvailableError(booking.flight_id)
        
        # Check if user already has a booking for this flight
        existing_booking = self.booking_repo.find_existing_booking(user.id, booking.flight_id)
        if existing_booking:
            logger.warning(f"User {user.email} already has a booking for flight {booking.flight_id}")
            raise BookingAlreadyExistsError(user.id, booking.flight_id)
        
        # Create new booking
        new_booking = self.booking_repo.create(user.id, booking.flight_id)
        
        logger.info(f"Successfully created booking {new_booking.id} for user {user.email} on flight {flight.origin} to {flight.destination}")
        return new_booking
    
    def update_booking(self, user: User, booking_id: int, booking_update: BookingUpdate) -> Booking:
        """Update a booking for a user."""
        logger.debug(f"Updating booking {booking_id} for user {user.id} to status {booking_update.status}")
        
        # Get the booking
        booking = self.booking_repo.find_by_id(booking_id)
        if not booking:
            logger.warning(f"Booking {booking_id} not found for user {user.email}")
            raise BookingNotFoundError(booking_id)
        
        # Ensure user owns this booking
        if booking.user_id != user.id:
            logger.warning(f"User {user.email} attempted to access booking {booking_id} owned by user {booking.user_id}")
            raise AccessDeniedError("booking", booking_id, user.id)
        
        # Check if booking can be cancelled (only upcoming flights)
        if booking_update.status == "cancelled":
            if booking.status != "booked":
                logger.warning(f"User {user.email} attempted to cancel booking {booking_id} with status {booking.status}")
                raise BookingCannotBeCancelledError(booking_id, booking.status)
            
            flight = self.flight_repo.find_by_id(booking.flight_id)
            if flight.departure_time <= datetime.datetime.now(datetime.timezone.utc):
                logger.warning(f"User {user.email} attempted to cancel past flight booking {booking_id}")
                raise PastFlightCannotBeCancelledError(booking_id, flight.id)
            
            cancelled_at = datetime.datetime.now(datetime.timezone.utc)
            updated_booking = self.booking_repo.update_status(booking_id, "cancelled", cancelled_at)
            logger.info(f"User {user.email} cancelled booking {booking_id} for flight {flight.origin} to {flight.destination}")
        else:
            updated_booking = self.booking_repo.update_status(booking_id, booking_update.status)
            logger.info(f"User {user.email} updated booking {booking_id} status to {booking_update.status}")
        
        return updated_booking
    
    def delete_booking(self, user: User, booking_id: int) -> Dict[str, str]:
        """Delete/cancel a booking for a user."""
        logger.debug(f"Deleting booking {booking_id} for user {user.id}")
        
        # Get the booking
        booking = self.booking_repo.find_by_id(booking_id)
        if not booking:
            logger.warning(f"Booking {booking_id} not found for user {user.email}")
            raise BookingNotFoundError(booking_id)
        
        # Ensure user owns this booking
        if booking.user_id != user.id:
            logger.warning(f"User {user.email} attempted to delete booking {booking_id} owned by user {booking.user_id}")
            raise AccessDeniedError("booking", booking_id, user.id)
        
        # Check if booking can be cancelled (only upcoming flights)
        if booking.status != "booked":
            logger.warning(f"User {user.email} attempted to delete booking {booking_id} with status {booking.status}")
            raise BookingCannotBeCancelledError(booking_id, booking.status)
        
        flight = self.flight_repo.find_by_id(booking.flight_id)
        if flight.departure_time <= datetime.datetime.now(datetime.timezone.utc):
            logger.warning(f"User {user.email} attempted to delete past flight booking {booking_id}")
            raise PastFlightCannotBeCancelledError(booking_id, flight.id)
        
        # Mark as cancelled instead of deleting
        cancelled_at = datetime.datetime.now(datetime.timezone.utc)
        self.booking_repo.update_status(booking_id, "cancelled", cancelled_at)
        
        logger.info(f"User {user.email} successfully deleted/cancelled booking {booking_id} for flight {flight.origin} to {flight.destination}")
        return {"message": "Booking cancelled successfully"}
    
    def get_user_bookings(self, user: User, status: Optional[str] = None) -> List[Booking]:
        """Get all bookings for a user with optional status filter."""
        logger.debug(f"Retrieving bookings for user {user.id} with status filter: {status}")
        
        bookings = self.booking_repo.find_by_user_id(user.id, status)
        
        logger.info(f"Successfully retrieved {len(bookings)} bookings for user {user.email} with status filter: {status}")
        logger.debug(f"Retrieved booking IDs: {[booking.id for booking in bookings]}")
        
        return bookings


def create_booking_service(
    booking_repo: BookingRepository = Depends(create_booking_repository),
    flight_repo: FlightRepository = Depends(create_flight_repository)
) -> BookingService:
    """Dependency injection function to create BookingService instance."""
    return BookingBusinessService(booking_repo, flight_repo)
