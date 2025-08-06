from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from fastapi import Depends
from repository import User, Booking
from schemas import BookingCreate, BookingUpdate, BookingResponse, FlightResponse, PaginatedResponse
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
    def create_booking(self, user: User, booking: BookingCreate) -> BookingResponse:
        """Create a new booking for a user."""
        pass
    
    @abstractmethod
    def update_booking(self, user: User, booking_id: int, booking_update: BookingUpdate) -> BookingResponse:
        """Update a booking for a user."""
        pass
    
    @abstractmethod
    def delete_booking(self, user: User, booking_id: int) -> Dict[str, str]:
        """Delete/cancel a booking for a user."""
        pass
    
    @abstractmethod
    def get_user_bookings(self, user: User, status: Optional[str] = None, 
                         booked_date: Optional[str] = None, departure_date: Optional[str] = None, 
                         page: int = 1, size: int = 10) -> PaginatedResponse[BookingResponse]:
        """Get all bookings for a user with optional filters and pagination."""
        pass
    
    @abstractmethod
    def get_computed_booking_status(self, booking: Booking) -> str:
        """Get the computed status for a booking (considering flight departure time)."""
        pass


class BookingBusinessService(BookingService):
    """Implementation of BookingService with business logic."""
    
    def __init__(self, booking_repo: BookingRepository, flight_repo: FlightRepository):
        self.booking_repo = booking_repo
        self.flight_repo = flight_repo
    
    def _convert_booking_to_response(self, booking: Booking) -> BookingResponse:
        """Convert Booking model to BookingResponse schema."""
        # Convert flight to FlightResponse
        flight_response = FlightResponse(
            id=booking.flight.id,
            origin=booking.flight.origin,
            destination=booking.flight.destination,
            departure_time=booking.flight.departure_time,
            arrival_time=booking.flight.arrival_time,
            airline=booking.flight.airline,
            status=booking.flight.status,
            price=booking.flight.price
        )
        
        # Determine computed status
        computed_status = self.get_computed_booking_status(booking)
        
        # Convert booking to BookingResponse
        return BookingResponse(
            id=booking.id,
            flight_id=booking.flight_id,
            status=computed_status,
            booked_at=booking.booked_at,
            cancelled_at=booking.cancelled_at,
            flight=flight_response
        )
    
    def create_booking(self, user: User, booking: BookingCreate) -> BookingResponse:
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
        
        # Convert Booking model to BookingResponse schema
        return self._convert_booking_to_response(new_booking)
    
    def update_booking(self, user: User, booking_id: int, booking_update: BookingUpdate) -> BookingResponse:
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
            # Ensure timezone-aware comparison by treating departure_time as UTC
            departure_time_utc = flight.departure_time.replace(tzinfo=datetime.timezone.utc) if flight.departure_time.tzinfo is None else flight.departure_time
            if departure_time_utc <= datetime.datetime.now(datetime.timezone.utc):
                logger.warning(f"User {user.email} attempted to cancel past flight booking {booking_id}")
                raise PastFlightCannotBeCancelledError(booking_id, flight.id)
            
            cancelled_at = datetime.datetime.now(datetime.timezone.utc)
            updated_booking = self.booking_repo.update_status(booking_id, "cancelled", cancelled_at)
            logger.info(f"User {user.email} cancelled booking {booking_id} for flight {flight.origin} to {flight.destination}")
        else:
            updated_booking = self.booking_repo.update_status(booking_id, booking_update.status)
            logger.info(f"User {user.email} updated booking {booking_id} status to {booking_update.status}")
        
        # Convert Booking model to BookingResponse schema
        return self._convert_booking_to_response(updated_booking)
    
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
        # Ensure timezone-aware comparison by treating departure_time as UTC
        departure_time_utc = flight.departure_time.replace(tzinfo=datetime.timezone.utc) if flight.departure_time.tzinfo is None else flight.departure_time
        if departure_time_utc <= datetime.datetime.now(datetime.timezone.utc):
            logger.warning(f"User {user.email} attempted to delete past flight booking {booking_id}")
            raise PastFlightCannotBeCancelledError(booking_id, flight.id)
        
        # Mark as cancelled instead of deleting
        cancelled_at = datetime.datetime.now(datetime.timezone.utc)
        self.booking_repo.update_status(booking_id, "cancelled", cancelled_at)
        
        logger.info(f"User {user.email} successfully deleted/cancelled booking {booking_id} for flight {flight.origin} to {flight.destination}")
        return {"message": "Booking cancelled successfully"}
    
    def get_computed_booking_status(self, booking: Booking) -> str:
        """Get the computed status for a booking (considering flight departure time)."""
        # If already cancelled, return cancelled
        if booking.status == "cancelled":
            return "cancelled"
        
        # Check if flight has departed
        departure_time_utc = booking.flight.departure_time.replace(tzinfo=datetime.timezone.utc) if booking.flight.departure_time.tzinfo is None else booking.flight.departure_time
        if departure_time_utc <= datetime.datetime.now(datetime.timezone.utc):
            return "completed"
        
        # Otherwise, it's booked (upcoming)
        return "booked"
    
    def get_user_bookings(self, user: User, status: Optional[str] = None, 
                         booked_date: Optional[str] = None, departure_date: Optional[str] = None, 
                         page: int = 1, size: int = 10) -> PaginatedResponse[BookingResponse]:
        """Get all bookings for a user with optional filters and pagination."""
        logger.debug(f"Retrieving bookings for user {user.id} with status filter: {status}, booked_date: {booked_date}, departure_date: {departure_date}, page: {page}, size: {size}")
        
        bookings, total = self.booking_repo.find_by_user_id_paginated(
            user.id, status, booked_date, departure_date, page, size
        )
        
        logger.info(f"Successfully retrieved {len(bookings)} bookings for user {user.email} (total: {total})")
        logger.debug(f"Retrieved booking IDs: {[booking.id for booking in bookings]}")
        
        # Convert Booking models to BookingResponse schemas
        booking_responses = [self._convert_booking_to_response(booking) for booking in bookings]
        
        # Calculate total pages
        pages = (total + size - 1) // size
        
        return PaginatedResponse(
            items=booking_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


def create_booking_service(
    booking_repo: BookingRepository = Depends(create_booking_repository),
    flight_repo: FlightRepository = Depends(create_flight_repository)
) -> BookingService:
    """Dependency injection function to create BookingService instance."""
    return BookingBusinessService(booking_repo, flight_repo)
