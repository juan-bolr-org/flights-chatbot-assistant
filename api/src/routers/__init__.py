from .users import router as users_router
from .flights import router as flights_router
from .bookings import router as bookings_router
from .chat import router as chat_router
from .health_check import router as health_check_router
from .speech import router as speech_router

__all__ = ["users_router", "flights_router", "bookings_router", "chat_router", "health_check_router", "speech_router"]
