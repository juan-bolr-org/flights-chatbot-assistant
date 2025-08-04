from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from schemas import BookingCreate, BookingResponse, BookingUpdate
from models import User, Flight, Booking
from resources.dependencies import get_database_session as get_db, get_current_user
from resources.logging import get_logger

router = APIRouter(prefix="/bookings", tags=["bookings"])
logger = get_logger("bookings_router")

@router.post("", response_model=BookingResponse)
def create_booking(
    booking: BookingCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Creating booking for user {current_user.id}, flight {booking.flight_id}")
        
        # Check if flight exists and is available
        flight = db.query(Flight).filter(Flight.id == booking.flight_id, Flight.status == "scheduled").first()
        if not flight:
            logger.warning(f"Flight {booking.flight_id} not found or not available for user {current_user.email}")
            raise HTTPException(status_code=404, detail="Flight not found or not available")
        
        # Check if user already has a booking for this flight
        existing_booking = db.query(Booking).filter(
            Booking.user_id == current_user.id,
            Booking.flight_id == booking.flight_id,
            Booking.status == "booked"
        ).first()
        if existing_booking:
            logger.warning(f"User {current_user.email} already has a booking for flight {booking.flight_id}")
            raise HTTPException(status_code=400, detail="You already have a booking for this flight")
        
        # Create new booking
        new_booking = Booking(
            user_id=current_user.id,
            flight_id=booking.flight_id,
            status="booked"
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        
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
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Updating booking {booking_id} for user {current_user.id} to status {booking_update.status}")
        
        # Get the booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
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
            
            flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
            if flight.departure_time <= datetime.datetime.now():
                logger.warning(f"User {current_user.email} attempted to cancel past flight booking {booking_id}")
                raise HTTPException(status_code=400, detail="Cannot cancel past flights")
            
            booking.status = "cancelled"
            booking.cancelled_at = datetime.datetime.now(datetime.UTC)
            logger.info(f"User {current_user.email} cancelled booking {booking_id} for flight {flight.origin} to {flight.destination}")
        else:
            booking.status = booking_update.status
            logger.info(f"User {current_user.email} updated booking {booking_id} status to {booking_update.status}")
        
        db.commit()
        db.refresh(booking)
        return booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking {booking_id} for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error updating booking: {str(e)}"
        )

@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        logger.debug(f"Deleting booking {booking_id} for user {current_user.id}")
        
        # Get the booking
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
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
        
        flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
        if flight.departure_time <= datetime.datetime.now(datetime.UTC):
            logger.warning(f"User {current_user.email} attempted to delete past flight booking {booking_id}")
            raise HTTPException(status_code=400, detail="Cannot cancel past flights")
        
        # Mark as cancelled instead of deleting
        booking.status = "cancelled"
        booking.cancelled_at = datetime.datetime.now(datetime.UTC)
        db.commit()
        
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
    db: Session = Depends(get_db)
):  
    try:
        logger.debug(f"Retrieving bookings for user {current_user.id} with status filter: {status}")
        
        query = db.query(Booking).filter(Booking.user_id == current_user.id)
        
        if status:
            if status == "upcoming":
                # Show booked flights that haven't departed yet
                query = query.join(Flight).filter(
                    Booking.status == "booked",
                    Flight.departure_time > datetime.datetime.now(datetime.UTC)
                )
            elif status == "past":
                # Show flights that have departed or been cancelled
                query = query.join(Flight).filter(
                    (Flight.departure_time <= datetime.datetime.now(datetime.UTC)) |
                    (Booking.status == "cancelled")
                )
            else:
                query = query.filter(Booking.status == status)
        
        bookings = query.order_by(Booking.booked_at.desc()).all()
        
        logger.info(f"Successfully retrieved {len(bookings)} bookings for user {current_user.email} with status filter: {status}")
        logger.debug(f"Retrieved booking IDs: {[booking.id for booking in bookings]}")
        
        return bookings
        
    except Exception as e:
        logger.error(f"Error retrieving bookings for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving bookings: {str(e)}"
        )
