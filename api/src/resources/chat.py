from langchain.chat_models import init_chat_model
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from utils.chatbot_tools import create_faqs_retriever_tool, create_chatbot_tools
from typing import Optional, List
from pydantic import BaseModel, Field
import re
import os
import uuid
import aiosqlite
from .logging import get_logger
from constants import ApplicationConstants, EnvironmentKeys, get_env_str

logger = get_logger("chat")


class ChatConfig(BaseModel):
    """Chat configuration with Pydantic validation."""
    model_name: str = Field(default="openai:gpt-4.1", description="LLM model name")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Model temperature")
    checkpoint_db_path: str = Field(
        default_factory=lambda: get_env_str(
            EnvironmentKeys.CHAT_CHECKPOINT_DB, 
            ApplicationConstants.DEFAULT_CHAT_CHECKPOINT_DB
        ),
        description="SQLite database path for chat checkpoints"
    )
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
        self.memory: Optional[AsyncSqliteSaver] = None
        self.agent: Optional[object] = None  # The react agent
        self._is_initialized: bool = False
        self._memory_context = None  # Store the context manager
    
    def initialize(self) -> None:
        """Initialize the chat model and related components (sync part only)."""
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
            
            self._is_initialized = True
            logger.info("Chat manager initialized successfully (sync part)")
            
        except Exception as e:
            logger.error(f"Error initializing chat manager: {e}", exc_info=True)
            raise
    
    async def ensure_memory_initialized(self) -> None:
        """Ensure the async memory component is initialized."""
        if self.memory is not None:
            return
            
        logger.debug(f"Initializing AsyncSQLite checkpointer: {self.config.checkpoint_db_path}")
        
        # Extract the database path from the connection string
        db_path = self.config.checkpoint_db_path
        if db_path.startswith("sqlite+aiosqlite:///"):
            db_path = db_path.replace("sqlite+aiosqlite:///", "")
        elif db_path.startswith("sqlite:///"):
            db_path = db_path.replace("sqlite:///", "")
        
        # Convert relative path to absolute path
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)
        
        # Ensure the directory exists for the database file
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.debug(f"Created directory for SQLite database: {db_dir}")
        
        # Use AsyncSqliteSaver.from_conn_string() as a context manager manually
        # Store the context manager for later cleanup
        # Note: from_conn_string expects just the file path, not a connection URI
        self._memory_context = AsyncSqliteSaver.from_conn_string(db_path)
        self.memory = await self._memory_context.__aenter__()
        
        logger.debug("AsyncSQLite checkpointer initialized successfully")
    
    async def cleanup(self) -> None:
        """Clean up resources, specifically close the AsyncSqliteSaver context manager."""
        if self._memory_context and self.memory:
            try:
                await self._memory_context.__aexit__(None, None, None)
                logger.debug("AsyncSqliteSaver context manager closed successfully")
            except Exception as e:
                logger.error(f"Error closing AsyncSqliteSaver context manager: {e}", exc_info=True)
        
        self.memory = None
        self._memory_context = None
        self._is_initialized = False
    
    async def create_agent(self, user_token: str, user_id: int, session_id: Optional[str] = None) -> CompiledStateGraph:
        """Create and return a configured react agent for the user with optional session ID."""
        if not self._is_initialized:
            self.initialize()
        
        await self.ensure_memory_initialized()
        
        try:
            from constants import ApplicationConstants, EnvironmentKeys, get_env_int
            api_base_port = get_env_int(EnvironmentKeys.PORT, ApplicationConstants.DEFAULT_PORT)
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
    
    async def get_memory(self) -> AsyncSqliteSaver:
        """Get the AsyncSQLite checkpointer."""
        if not self._is_initialized:
            self.initialize()
        await self.ensure_memory_initialized()
        return self.memory
    
    def get_system_context(self) -> str:
        """Get the normalized system context."""
        return re.sub(r"\s+", " ", self.config.system_context).strip()
    
    def generate_session_id(self, user_id: int, session_name: str) -> str:
        """Generate a deterministic session ID for a user with a session name."""
        # Clean session name for use in ID
        clean_name = ''.join(c for c in session_name if c.isalnum() or c in '_-').lower()
        return f"{user_id}_{clean_name}"
    
    async def get_user_sessions(self, user_id: int) -> List[str]:
        """Get all session IDs for a specific user from the checkpoint database."""
        if not self._is_initialized:
            self.initialize()
        
        await self.ensure_memory_initialized()
        
        try:
            # Get all sessions from the checkpointer that belong to this user
            prefix = f"{user_id}_"
            sessions = []
            
            # Extract the database path from the connection string
            db_path = self.config.checkpoint_db_path
            if db_path.startswith("sqlite+aiosqlite:///"):
                db_path = db_path.replace("sqlite+aiosqlite:///", "")
            elif db_path.startswith("sqlite:///"):
                db_path = db_path.replace("sqlite:///", "")
            
            # Convert relative path to absolute path
            if not os.path.isabs(db_path):
                db_path = os.path.abspath(db_path)
            
            # Query the database directly for sessions
            async with aiosqlite.connect(db_path) as conn:
                cursor = await conn.cursor()
                # Check if the checkpoints table exists
                await cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='checkpoints'
                """)
                if await cursor.fetchone():
                    await cursor.execute("""
                        SELECT DISTINCT thread_id FROM checkpoints 
                        WHERE thread_id LIKE ?
                    """, (f"{prefix}%",))
                    rows = await cursor.fetchall()
                    sessions = [row[0] for row in rows]
            
            return sessions
            
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {e}", exc_info=True)
            return []


# Global instance - Singleton pattern
chat_manager = ChatManager()
