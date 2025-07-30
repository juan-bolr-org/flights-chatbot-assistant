from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from schemas import BookingCreate, BookingResponse, BookingUpdate
from models import User, Flight, Booking
from utils import get_db, get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("", response_model=BookingResponse)
def create_booking(
    booking: BookingCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Check if flight exists and is available
    flight = db.query(Flight).filter(Flight.id == booking.flight_id, Flight.status == "scheduled").first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found or not available")
    
    # Check if user already has a booking for this flight
    existing_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.flight_id == booking.flight_id,
        Booking.status == "booked"
    ).first()
    if existing_booking:
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
    
    return new_booking

@router.patch("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int, 
    booking_update: BookingUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Get the booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Ensure user owns this booking
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if booking can be cancelled (only upcoming flights)
    if booking_update.status == "cancelled":
        if booking.status != "booked":
            raise HTTPException(status_code=400, detail="Only booked flights can be cancelled")
        
        flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
        if flight.departure_time <= datetime.datetime.now():
            raise HTTPException(status_code=400, detail="Cannot cancel past flights")
        
        booking.status = "cancelled"
        booking.cancelled_at = datetime.datetime.now(datetime.UTC)
    else:
        booking.status = booking_update.status
    
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Get the booking
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Ensure user owns this booking
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if booking can be cancelled (only upcoming flights)
    if booking.status != "booked":
        raise HTTPException(status_code=400, detail="Only booked flights can be cancelled")
    
    flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()
    if flight.departure_time <= datetime.datetime.now(datetime.UTC):
        raise HTTPException(status_code=400, detail="Cannot cancel past flights")
    
    # Mark as cancelled instead of deleting
    booking.status = "cancelled"
    booking.cancelled_at = datetime.datetime.now(datetime.UTC)
    db.commit()
    
    return {"message": "Booking cancelled successfully"}

@router.get("/user/{user_id}", response_model=List[BookingResponse])
def get_user_bookings(
    user_id: int, 
    status: Optional[str] = None, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Ensure user can only access their own bookings
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(Booking).filter(Booking.user_id == user_id)
    
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
    return bookings
