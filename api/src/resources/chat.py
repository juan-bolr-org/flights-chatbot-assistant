from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from utils.chatbot_tools import create_faqs_retriever_tool, create_chatbot_tools
from typing import Optional, List
from pydantic import BaseModel, Field
import re
import os
from .logging import get_logger

logger = get_logger("chat")


class ChatConfig(BaseModel):
    """Chat configuration with Pydantic validation."""
    model_name: str = Field(default="openai:gpt-4.1", description="LLM model name")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Model temperature")
    system_context: str = Field(
        default="""
            You are a helpful flight booking assistant. You have access to several tools:
            1. flight_faqs: Use this for general flight information, policies, FAQ, baggage rules, check-in procedures, etc.
            2. search_flights: Use this to search for available flights based on specific criteria
            3. list_all_flights: Use this to show all available flights
            4. book_flight: Use this to make flight reservations
            5. get_my_bookings: Use this to show user's current bookings
            6. cancel_booking: Use this to cancel existing bookings
            You can also help users with travel-related recommendations, trip planning, and general advice for their journeys. However, please clarify to users that any information or suggestions outside the scope of these tools may be outdated or inaccurate, and they should verify such details independently.
            Always be helpful and provide accurate information. If you need to search for flights or manage bookings, use the appropriate API tools. For general questions about flight policies or procedures, use the flight_faqs tool.
        """,
        description="System context for the chat model"
    )


class ChatManager:
    """Manages chat model initialization and configuration."""
    
    def __init__(self, config: Optional[ChatConfig] = None) -> None:
        self.config: ChatConfig = config or ChatConfig()
        self.response_model: Optional[BaseChatModel] = None
        self.faq_tool: Optional[object] = None  # Type will depend on the tool implementation
        self.memory: Optional[MemorySaver] = None
        self.agent: Optional[object] = None  # The react agent
        self._is_initialized: bool = False
    
    def initialize(self) -> None:
        """Initialize the chat model and related components."""
        if self._is_initialized:
            return
        
        logger.info("Initializing chat manager...")
        try:
            # Create retriever tool
            logger.debug("Creating FAQ retriever tool...")
            self.faq_tool = create_faqs_retriever_tool()
            
            # Initialize chat model
            logger.debug(f"Initializing chat model: {self.config.model_name}")
            self.response_model = init_chat_model(
                self.config.model_name, 
                temperature=self.config.temperature
            )
            
            # Initialize memory saver
            logger.debug("Initializing memory saver...")
            self.memory = MemorySaver()
            
            self._is_initialized = True
            logger.info("Chat manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing chat manager: {e}", exc_info=True)
            raise
    
    def create_agent(self, user_token: str, user_id: int) -> CompiledStateGraph:
        """Create and return a configured react agent for the user."""
        if not self._is_initialized:
            self.initialize()
        
        try:
            api_base_port = os.getenv("PORT", "8000")
            api_base_url = f"http://localhost:{api_base_port}"
            
            logger.debug(f"Creating chatbot tools for user {user_id}")
            chatbot_tools = create_chatbot_tools(
                user_token=user_token,
                user_id=user_id,
                api_base_url=api_base_url,
            )
            
            # Add FAQ tool if available
            if self.faq_tool is not None:
                chatbot_tools = chatbot_tools + [self.faq_tool]
                logger.debug("Added FAQ tool to chatbot tools")
            else:
                logger.warning("No FAQ tool available, skipping...")

            logger.debug("Creating react agent...")
            agent = create_react_agent(
                tools=chatbot_tools,
                model=self.response_model,
                checkpointer=self.memory
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"Error creating agent for user {user_id}: {e}", exc_info=True)
            raise
    
    def get_response_model(self) -> BaseChatModel:
        """Get the initialized response model."""
        if not self._is_initialized:
            self.initialize()
        return self.response_model
    
    def get_faq_tool(self) -> object:
        """Get the FAQ retriever tool."""
        if not self._is_initialized:
            self.initialize()
        return self.faq_tool
    
    def get_memory(self) -> MemorySaver:
        """Get the memory saver."""
        if not self._is_initialized:
            self.initialize()
        return self.memory
    
    def get_system_context(self) -> str:
        """Get the normalized system context."""
        if not self._is_initialized:
            self.initialize()
        return re.sub(r"\s+", " ", self.config.system_context).strip()


# Global instance - Singleton pattern
chat_manager = ChatManager()
