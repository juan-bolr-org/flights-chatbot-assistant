from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from repository.user import User
from schemas import BookingCreate, BookingResponse, BookingUpdate
from resources.dependencies import get_current_user
from resources.logging import get_logger
from repository import BookingRepository, FlightRepository, create_booking_repository, create_flight_repository

router = APIRouter(prefix="/bookings", tags=["bookings"])
logger = get_logger("bookings_router")

@router.post("", response_model=BookingResponse)
def create_booking(
    booking: BookingCreate, 
    current_user: User = Depends(get_current_user), 
    booking_repo: BookingRepository = Depends(create_booking_repository),
    flight_repo: FlightRepository = Depends(create_flight_repository)
):
    try:
        logger.debug(f"Creating booking for user {current_user.id}, flight {booking.flight_id}")
        
        # Check if flight exists and is available
        flight = flight_repo.find_available_by_id(booking.flight_id)
        if not flight:
            logger.warning(f"Flight {booking.flight_id} not found or not available for user {current_user.email}")
            raise HTTPException(status_code=404, detail="Flight not found or not available")
        
        # Check if user already has a booking for this flight
        existing_booking = booking_repo.find_existing_booking(current_user.id, booking.flight_id)
        if existing_booking:
            logger.warning(f"User {current_user.email} already has a booking for flight {booking.flight_id}")
            raise HTTPException(status_code=400, detail="You already have a booking for this flight")
        
        # Create new booking
        new_booking = booking_repo.create(current_user.id, booking.flight_id)
        
        logger.info(f"Successfully created booking {new_booking.id} for user {current_user.email} on flight {flight.origin} to {flight.destination}")
        return new_booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error creating booking: {str(e)}"
        )

@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int, 
    booking_update: BookingUpdate, 
    current_user: User = Depends(get_current_user), 
    booking_repo: BookingRepository = Depends(create_booking_repository),
    flight_repo: FlightRepository = Depends(create_flight_repository)
):
    try:
        logger.debug(f"Updating booking {booking_id} for user {current_user.id} to status {booking_update.status}")
        
        # Get the booking
        booking = booking_repo.find_by_id(booking_id)
        if not booking:
            logger.warning(f"Booking {booking_id} not found for user {current_user.email}")
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Ensure user owns this booking
        if booking.user_id != current_user.id:
            logger.warning(f"User {current_user.email} attempted to access booking {booking_id} owned by user {booking.user_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if booking can be cancelled (only upcoming flights)
        if booking_update.status == "cancelled":
            if booking.status != "booked":
                logger.warning(f"User {current_user.email} attempted to cancel booking {booking_id} with status {booking.status}")
                raise HTTPException(status_code=400, detail="Only booked flights can be cancelled")
            
            flight = flight_repo.find_by_id(booking.flight_id)
            if flight.departure_time <= datetime.datetime.now():
                logger.warning(f"User {current_user.email} attempted to cancel past flight booking {booking_id}")
                raise HTTPException(status_code=400, detail="Cannot cancel past flights")
            
            cancelled_at = datetime.datetime.now(datetime.UTC)
            updated_booking = booking_repo.update_status(booking_id, "cancelled", cancelled_at)
            logger.info(f"User {current_user.email} cancelled booking {booking_id} for flight {flight.origin} to {flight.destination}")
        else:
            updated_booking = booking_repo.update_status(booking_id, booking_update.status)
            logger.info(f"User {current_user.email} updated booking {booking_id} status to {booking_update.status}")
        
        return updated_booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking {booking_id} for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error updating booking: {str(e)}"
        )@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int, 
    current_user: User = Depends(get_current_user), 
    booking_repo: BookingRepository = Depends(create_booking_repository),
    flight_repo: FlightRepository = Depends(create_flight_repository)
):
    try:
        logger.debug(f"Deleting booking {booking_id} for user {current_user.id}")
        
        # Get the booking
        booking = booking_repo.find_by_id(booking_id)
        if not booking:
            logger.warning(f"Booking {booking_id} not found for user {current_user.email}")
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Ensure user owns this booking
        if booking.user_id != current_user.id:
            logger.warning(f"User {current_user.email} attempted to delete booking {booking_id} owned by user {booking.user_id}")
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if booking can be cancelled (only upcoming flights)
        if booking.status != "booked":
            logger.warning(f"User {current_user.email} attempted to delete booking {booking_id} with status {booking.status}")
            raise HTTPException(status_code=400, detail="Only booked flights can be cancelled")
        
        flight = flight_repo.find_by_id(booking.flight_id)
        if flight.departure_time <= datetime.datetime.now(datetime.UTC):
            logger.warning(f"User {current_user.email} attempted to delete past flight booking {booking_id}")
            raise HTTPException(status_code=400, detail="Cannot cancel past flights")
        
        # Mark as cancelled instead of deleting
        cancelled_at = datetime.datetime.now(datetime.UTC)
        booking_repo.update_status(booking_id, "cancelled", cancelled_at)
        
        logger.info(f"User {current_user.email} successfully deleted/cancelled booking {booking_id} for flight {flight.origin} to {flight.destination}")
        return {"message": "Booking cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting booking {booking_id} for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting booking: {str(e)}"
        )

@router.get("/user", response_model=List[BookingResponse])
def get_user_bookings(
    status: Optional[str] = None, 
    current_user: User = Depends(get_current_user), 
    booking_repo: BookingRepository = Depends(create_booking_repository)
):  
    try:
        logger.debug(f"Retrieving bookings for user {current_user.id} with status filter: {status}")
        
        bookings = booking_repo.find_by_user_id(current_user.id, status)
        
        logger.info(f"Successfully retrieved {len(bookings)} bookings for user {current_user.email} with status filter: {status}")
        logger.debug(f"Retrieved booking IDs: {[booking.id for booking in bookings]}")
        
        return bookings
        
    except Exception as e:
        logger.error(f"Error retrieving bookings for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving bookings: {str(e)}"
        )
