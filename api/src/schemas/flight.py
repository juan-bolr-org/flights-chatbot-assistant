from pydantic import BaseModel
from typing import Optional
import datetime

class FlightSearch(BaseModel):
    origin: str
    destination: str
    departure_date: str  # YYYY-MM-DD format

class FlightCreate(BaseModel):
    origin: str
    destination: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    airline: str
    status: Optional[str] = "scheduled"

class FlightResponse(BaseModel):
    id: int
    origin: str
    destination: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    airline: str
    status: str

    class Config:
        from_attributes = True
