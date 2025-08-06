from .user import UserCreate, UserLogin, UserResponse, Token
from .flight import FlightSearch, FlightResponse, FlightCreate
from .booking import BookingCreate, BookingResponse, BookingUpdate
from .chat import ChatRequest, ChatResponse, ChatMessageResponse, ChatHistoryResponse
from .speech import SpeechToTextResponse

__all__ = [
    "UserCreate",
    "UserLogin", 
    "UserResponse",
    "Token",
    "FlightSearch",
    "FlightResponse",
    "FlightCreate",
    "BookingCreate",
    "BookingResponse",
    "BookingUpdate",
    "ChatRequest",
    "ChatResponse",
    "ChatMessageResponse",
    "ChatHistoryResponse",
    "SpeechToTextResponse"
]
