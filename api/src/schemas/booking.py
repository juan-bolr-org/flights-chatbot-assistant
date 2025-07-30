from pydantic import BaseModel
from typing import Optional
import datetime
from .flight import FlightResponse

class BookingCreate(BaseModel):
    flight_id: int

class BookingResponse(BaseModel):
    id: int
    flight_id: int
    status: str
    booked_at: datetime.datetime
    cancelled_at: Optional[datetime.datetime] = None
    flight: FlightResponse

    class Config:
        from_attributes = True

class BookingUpdate(BaseModel):
    status: str
