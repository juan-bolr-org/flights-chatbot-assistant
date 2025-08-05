from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

import httpx
from langchain_core.tools import BaseTool
from langchain_core.callbacks import AsyncCallbackManagerForToolRun
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from resources.logging import get_logger

logger = get_logger("chatbot_tools")


# Pydantic models for tool arguments
class FlightSearchArgs(BaseModel):
    origin: str = Field(description="Origin airport code or city name")
    destination: str = Field(description="Destination airport code or city name")
    departure_date: str = Field(description="Departure date in YYYY-MM-DD format")


class BookingCreateArgs(BaseModel):
    flight_id: int = Field(description="The ID of the flight to book")


class BookingUpdateArgs(BaseModel):
    booking_id: int = Field(description="The ID of the booking to update")
    status: str = Field(description="New status for the booking (e.g., 'cancelled')")


class UserBookingsArgs(BaseModel):
    status: Optional[str] = Field(
        default=None,
        description="Filter bookings by status (upcoming, past, booked, cancelled)"
    )


class FlightSearchTool(BaseTool):
    """Tool to search for flights using the flights API."""
    
    name: str = "search_flights"
    description: str = (
        "Search for available flights based on origin, destination, and departure date. "
        "Useful when users ask about flight availability, schedules, or want to find flights."
    )
    args_schema: type[BaseModel] = FlightSearchArgs
    return_direct: bool = False
    user_token: str
    api_base_url: str

    def __init__(self, user_token: str, api_base_url: str, **kwargs):
        super().__init__(user_token=user_token, api_base_url=api_base_url, **kwargs)

    async def _arun(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Search for flights asynchronously."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/flights/search",
                    params={
                        "origin": origin,
                        "destination": destination,
                        "departure_date": departure_date
                    },
                    headers={"Authorization": f"Bearer {self.user_token}"}
                )
                
                if response.status_code == 200:
                    flights = response.json()
                    if not flights:
                        return f"No flights found from {origin} to {destination} on {departure_date}"
                    
                    result = f"Found {len(flights)} flights from {origin} to {destination} on {departure_date}:\n\n"
                    for flight in flights:
                        departure_time = datetime.fromisoformat(flight['departure_time'].replace('Z', '+00:00'))
                        arrival_time = datetime.fromisoformat(flight['arrival_time'].replace('Z', '+00:00'))
                        result += (
                            f"Flight ID: {flight['id']}\n"
                            f"Airline: {flight['airline']}\n"
                            f"Departure: {departure_time.strftime('%Y-%m-%d %H:%M')}\n"
                            f"Arrival: {arrival_time.strftime('%Y-%m-%d %H:%M')}\n"
                            f"Price: ${flight['price']}\n"
                            f"Status: {flight['status']}\n\n"
                        )
                    return result
                else:
                    return f"Error searching flights: {response.text}"
                    
        except Exception as e:
            return f"Error occurred while searching flights: {str(e)}"

    def _run(
        self,
        origin: str,
        destination: str, 
        departure_date: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Not implemented for sync execution."""
        raise NotImplementedError("This tool only supports async execution")


class ListFlightsTool(BaseTool):
    """Tool to list all available flights."""
    
    name: str = "list_all_flights"
    description: str = (
        "Get a list of all available flights. "
        "Useful when users want to see all flight options or browse available flights."
    )
    return_direct: bool = False
    user_token: str
    api_base_url: str

    def __init__(self, user_token: str, api_base_url: str, **kwargs):
        super().__init__(user_token=user_token, api_base_url=api_base_url, **kwargs)

    async def _arun(
        self,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """List all flights asynchronously."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/flights/list",
                    headers={"Authorization": f"Bearer {self.user_token}"}
                )
                
                if response.status_code == 200:
                    flights = response.json()
                    if not flights:
                        return "No flights available at the moment."
                    
                    result = f"Available flights ({len(flights)} total):\n\n"
                    for flight in flights[:10]:  # Limit to first 10 to avoid too long responses
                        departure_time = datetime.fromisoformat(flight['departure_time'].replace('Z', '+00:00'))
                        result += (
                            f"Flight ID: {flight['id']} | {flight['origin']} → {flight['destination']}\n"
                            f"Airline: {flight['airline']}\n"
                            f"Departure: {departure_time.strftime('%Y-%m-%d %H:%M')}\n"
                            f"Price: ${flight['price']} | Status: {flight['status']}\n\n"
                        )
                    
                    if len(flights) > 10:
                        result += f"... and {len(flights) - 10} more flights available."
                    
                    return result
                else:
                    return f"Error listing flights: {response.text}"
                    
        except Exception as e:
            return f"Error occurred while listing flights: {str(e)}"

    def _run(self, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Not implemented for sync execution."""
        raise NotImplementedError("This tool only supports async execution")


class CreateBookingTool(BaseTool):
    """Tool to create a new flight booking."""
    
    name: str = "book_flight"
    description: str = (
        "Book a flight for the current user. Requires a valid flight ID. "
        "Use this when users want to make a reservation or book a specific flight."
    )
    args_schema: type[BaseModel] = BookingCreateArgs
    return_direct: bool = False
    user_token: str
    api_base_url: str

    def __init__(self, user_token: str, api_base_url: str, **kwargs):
        super().__init__(user_token=user_token, api_base_url=api_base_url, **kwargs)

    async def _arun(
        self,
        flight_id: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Create a booking asynchronously."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/bookings",
                    json={"flight_id": flight_id},
                    headers={"Authorization": f"Bearer {self.user_token}"}
                )
                
                if response.status_code == 200:
                    booking = response.json()
                    flight_info = booking['flight']
                    departure_time = datetime.fromisoformat(flight_info['departure_time'].replace('Z', '+00:00'))
                    
                    return (
                        f"✅ Flight booked successfully!\n\n"
                        f"Booking ID: {booking['id']}\n"
                        f"Flight: {flight_info['origin']} → {flight_info['destination']}\n"
                        f"Airline: {flight_info['airline']}\n"
                        f"Departure: {departure_time.strftime('%Y-%m-%d %H:%M')}\n"
                        f"Price: ${flight_info['price']}\n"
                        f"Status: {booking['status']}\n"
                        f"Booked at: {booking['booked_at']}"
                    )
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    return f"❌ Failed to book flight: {error_detail}"
                    
        except Exception as e:
            return f"Error occurred while booking flight: {str(e)}"

    def _run(
        self,
        flight_id: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Not implemented for sync execution."""
        raise NotImplementedError("This tool only supports async execution")


class GetUserBookingsTool(BaseTool):
    """Tool to get user's bookings."""
    
    name: str = "get_my_bookings"
    description: str = (
        "Get the current user's flight bookings. Can filter by status (upcoming, past, booked, cancelled). "
        "Use this when users ask about their reservations, bookings, or travel history."
    )
    args_schema: type[BaseModel] = UserBookingsArgs
    return_direct: bool = False
    user_token: str
    user_id: int
    api_base_url: str

    def __init__(self, user_token: str, user_id: int, api_base_url: str, **kwargs):
        super().__init__(user_token=user_token, user_id=user_id, api_base_url=api_base_url, **kwargs)

    async def _arun(
        self,
        status: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Get user bookings asynchronously."""
        try:
            async with httpx.AsyncClient() as client:
                params = {}
                if status:
                    params["status"] = status
                    
                response = await client.get(
                    f"{self.api_base_url}/bookings/user",
                    params=params,
                    headers={"Authorization": f"Bearer {self.user_token}"}
                )
                
                if response.status_code == 200:
                    bookings = response.json()
                    if not bookings:
                        status_text = f" with status '{status}'" if status else ""
                        return f"You have no bookings{status_text}."
                    
                    result = f"Your bookings{' (' + status + ')' if status else ''} ({len(bookings)} total):\n\n"
                    for booking in bookings:
                        flight_info = booking['flight']
                        departure_time = datetime.fromisoformat(flight_info['departure_time'].replace('Z', '+00:00'))
                        booked_time = datetime.fromisoformat(booking['booked_at'].replace('Z', '+00:00'))
                        
                        result += (
                            f"Booking ID: {booking['id']}\n"
                            f"Flight: {flight_info['origin']} → {flight_info['destination']}\n"
                            f"Airline: {flight_info['airline']}\n"
                            f"Departure: {departure_time.strftime('%Y-%m-%d %H:%M')}\n"
                            f"Price: ${flight_info['price']}\n"
                            f"Status: {booking['status']}\n"
                            f"Booked: {booked_time.strftime('%Y-%m-%d %H:%M')}\n"
                        )
                        
                        if booking.get('cancelled_at'):
                            cancelled_time = datetime.fromisoformat(booking['cancelled_at'].replace('Z', '+00:00'))
                            result += f"Cancelled: {cancelled_time.strftime('%Y-%m-%d %H:%M')}\n"
                        
                        result += "\n"
                    
                    return result
                else:
                    return f"Error retrieving bookings: {response.text}"
                    
        except Exception as e:
            return f"Error occurred while retrieving bookings: {str(e)}"

    def _run(
        self,
        status: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Not implemented for sync execution."""
        raise NotImplementedError("This tool only supports async execution")


class CancelBookingTool(BaseTool):
    """Tool to cancel a booking."""
    
    name: str = "cancel_booking"
    description: str = (
        "Cancel a user's flight booking. Requires the booking ID. "
        "Use this when users want to cancel their reservations or modify bookings to cancelled status."
    )
    args_schema: type[BaseModel] = BookingUpdateArgs
    return_direct: bool = False
    user_token: str
    api_base_url: str

    def __init__(self, user_token: str, api_base_url: str, **kwargs):
        super().__init__(user_token=user_token, api_base_url=api_base_url, **kwargs)

    async def _arun(
        self,
        booking_id: int,
        status: str = "cancelled",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Cancel a booking asynchronously."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.api_base_url}/bookings/{booking_id}",
                    json={"status": status},
                    headers={"Authorization": f"Bearer {self.user_token}"}
                )
                
                if response.status_code == 200:
                    booking = response.json()
                    flight_info = booking['flight']
                    
                    return (
                        f"✅ Booking cancelled successfully!\n\n"
                        f"Booking ID: {booking['id']}\n"
                        f"Flight: {flight_info['origin']} → {flight_info['destination']}\n"
                        f"Airline: {flight_info['airline']}\n"
                        f"Status: {booking['status']}\n"
                        f"Cancelled at: {booking.get('cancelled_at', 'Just now')}"
                    )
                else:
                    error_detail = response.json().get('detail', 'Unknown error')
                    return f"❌ Failed to cancel booking: {error_detail}"
                    
        except Exception as e:
            return f"Error occurred while cancelling booking: {str(e)}"

    def _run(
        self,
        booking_id: int,
        status: str = "cancelled",
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Not implemented for sync execution."""
        raise NotImplementedError("This tool only supports async execution")


def create_chatbot_tools(user_token: str, user_id: int, api_base_url: str) -> List[BaseTool]:
    """Create and return a list of chatbot tools for the given user."""
    return [
        FlightSearchTool(user_token=user_token, api_base_url=api_base_url),
        ListFlightsTool(user_token=user_token, api_base_url=api_base_url),
        CreateBookingTool(user_token=user_token, api_base_url=api_base_url),
        GetUserBookingsTool(user_token=user_token, user_id=user_id, api_base_url=api_base_url),
        CancelBookingTool(user_token=user_token, api_base_url=api_base_url),
    ]


def create_faqs_retriever_tool():
    """Create and return a retriever tool for airline FAQs."""
    faqs = [
        "What is the baggage allowance for domestic flights? Each passenger is allowed one checked bag up to 23kg and one carry-on bag up to 8kg.",
        "How early should I arrive at the airport before my flight? It is recommended to arrive at least 2 hours before domestic flights and 3 hours before international flights.",
        "Can I change my flight after booking? Yes, you can change your flight up to 24 hours before departure, subject to availability and fare difference.",
        "What items are prohibited in carry-on luggage? Prohibited items include liquids over 100ml, sharp objects, and flammable materials.",
        "How do I check in online? Visit our website or mobile app, enter your booking reference, and follow the instructions to check in online.",
        "What should I do if my flight is delayed or cancelled? You will be notified via email or SMS. You can rebook or request a refund through our customer service.",
        "Are pets allowed on board? Small pets are allowed in the cabin with prior reservation. Larger pets must travel in the cargo hold.",
        "Do you offer special assistance for passengers with reduced mobility? Yes, please contact our support team at least 48 hours before your flight to arrange assistance.",
        "Can I select my seat in advance? Yes, seat selection is available during booking and online check-in, subject to availability.",
        "What is the policy for unaccompanied minors? Children aged 5-12 can travel alone with our unaccompanied minor service. Additional fees apply.",
        # Answers to chatbot capabilities
        "What can I ask the chatbot? You can ask about flight availability, booking flights, checking your bookings, cancelling flights, and general airline FAQs.",
        "Can I book a flight through the chatbot? Yes, you can book flights by providing the flight ID and confirming your booking.",
        "How do I cancel a booking using the chatbot? You can cancel a booking by providing the booking ID and confirming the cancellation.",
        "Can the chatbot help me find flights? Yes, you can search for flights by providing the origin, destination, and departure date.",
        "How do I check my bookings with the chatbot? You can retrieve your bookings by asking for your flight reservations, optionally filtering by status.",
        "What information do I need to book a flight? You need the flight ID to book a flight through the chatbot.",
        "Can I change my booking status using the chatbot? Yes, you can update your booking status to cancelled or other statuses as needed.",
    ]
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=200, chunk_overlap=20
    )
    faq_chunks = text_splitter.create_documents(faqs)
    vectorstore = InMemoryVectorStore.from_documents(
        documents=faq_chunks, embedding=OpenAIEmbeddings()
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    retriever_tool = create_retriever_tool(
        retriever,
        "flight_faqs",
        "Search through airline FAQs for baggage, check-in, delays, pets, seat selection, and more.",
    )
    return retriever_tool
