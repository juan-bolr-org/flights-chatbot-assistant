from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
import datetime

T = TypeVar('T')

class FlightSearch(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[str] = None  # YYYY-MM-DD format

class PaginationParams(BaseModel):
    page: int = 1
    size: int = 10

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class FlightCreate(BaseModel):
    origin: str
    destination: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    airline: str
    status: Optional[str] = "scheduled"
    price: float

class FlightResponse(BaseModel):
    id: int
    origin: str
    destination: str
    departure_time: datetime.datetime
    arrival_time: datetime.datetime
    airline: str
    status: str
    price: float

    class Config:
        from_attributes = True
