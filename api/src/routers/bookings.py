from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from repository import User
from schemas import BookingCreate, BookingResponse, BookingUpdate, PaginatedResponse
from resources.dependencies import get_current_user
from resources.logging import get_logger
from services import BookingService, create_booking_service
from exceptions import ApiException
from utils.error_handlers import api_exception_to_http_exception

router = APIRouter(prefix="/bookings", tags=["bookings"])
logger = get_logger("bookings_router")

@router.post("", response_model=BookingResponse)
def create_booking(
    booking: BookingCreate, 
    current_user: User = Depends(get_current_user), 
    booking_service: BookingService = Depends(create_booking_service)
):
    try:
        new_booking = booking_service.create_booking(current_user, booking)
        return new_booking
        
    except ApiException as e:
        logger.warning(f"Business logic error for user {current_user.email}: {e.error_code.value}")
        raise api_exception_to_http_exception(e)
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
    booking_service: BookingService = Depends(create_booking_service)
):
    try:
        updated_booking = booking_service.update_booking(current_user, booking_id, booking_update)
        return updated_booking
        
    except ApiException as e:
        logger.warning(f"Business logic error for user {current_user.email}: {e.error_code.value}")
        raise api_exception_to_http_exception(e)
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
    booking_service: BookingService = Depends(create_booking_service)
):
    try:
        result = booking_service.delete_booking(current_user, booking_id)
        return result
        
    except ApiException as e:
        logger.warning(f"Business logic error for user {current_user.email}: {e.error_code.value}")
        raise api_exception_to_http_exception(e)
    except Exception as e:
        logger.error(f"Error deleting booking {booking_id} for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting booking: {str(e)}"
        )

@router.get("/user", response_model=PaginatedResponse[BookingResponse])
def get_user_bookings(
    status: Optional[str] = Query(None, description="Filter by status: booked, cancelled, completed"), 
    booked_date: Optional[str] = Query(None, description="Filter by booking date (YYYY-MM-DD format)"),
    departure_date: Optional[str] = Query(None, description="Filter by departure date (YYYY-MM-DD format)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Page size"),
    current_user: User = Depends(get_current_user), 
    booking_service: BookingService = Depends(create_booking_service)
):  
    try:
        bookings = booking_service.get_user_bookings(current_user, status, booked_date, departure_date, page, size)
        return bookings
        
    except Exception as e:
        logger.error(f"Error retrieving bookings for user {current_user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving bookings: {str(e)}"
        )
