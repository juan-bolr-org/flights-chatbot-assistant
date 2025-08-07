from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from fastapi import Depends, Request
from repository import User
from schemas import (
    ChatRequest, ChatResponse, ChatHistoryResponse, ChatSessionsResponse, 
    DeleteSessionResponse, ChatMessageResponse, ChatSessionInfo,
    CreateSessionRequest, CreateSessionResponse, UpdateSessionAliasRequest, UpdateSessionAliasResponse
)
from resources.dependencies import get_system_context
from repository import (
    ChatbotMessageRepository, create_chatbot_message_repository,
    ChatSessionRepository, create_chat_session_repository
)
from resources.logging import get_logger
from resources.chat import chat_manager
from exceptions import AgentInvocationFailedError, ChatMessageSaveFailedError
import uuid

logger = get_logger("chat_service")


class ChatService(ABC):
    """Abstract base class for Chat service operations."""
    
    @abstractmethod
    async def process_chat_request(self, user: User, request: ChatRequest, jwt_token: str) -> ChatResponse:
        """Process a chat request and return response with session info."""
        pass
    
    @abstractmethod
    async def save_chat_message(self, user_id: int, session_id: str, message: str, response: str) -> None:
        """Save chat message to database."""
        pass
    
    @abstractmethod
    def get_chat_history(self, user_id: int, session_id: str, limit: int = 50, offset: int = 0) -> ChatHistoryResponse:
        """Get chat history for a specific session (session_id is now required)."""
        pass
    
    @abstractmethod
    def clear_chat_history(self, user_id: int, session_id: str) -> Dict[str, Any]:
        """Clear chat history for a specific session (session_id is now required)."""
        pass
    
    @abstractmethod
    async def get_user_sessions(self, user_id: int) -> ChatSessionsResponse:
        """Get all chat sessions for a user."""
        pass
    
    @abstractmethod
    def delete_session(self, user_id: int, session_id: str) -> DeleteSessionResponse:
        """Delete a specific chat session."""
        pass
    
    @abstractmethod
    async def create_session(self, user_id: int, request: CreateSessionRequest) -> CreateSessionResponse:
        """Create a new chat session."""
        pass
    
    @abstractmethod
    def update_session_alias(self, user_id: int, session_id: str, request: UpdateSessionAliasRequest) -> UpdateSessionAliasResponse:
        """Update session alias."""
        pass


class AgentChatService(ChatService):
    """Implementation of ChatService using LangChain agent with session support."""
    
    def __init__(self, system_context: str, chat_repo: ChatbotMessageRepository, session_repo: ChatSessionRepository):
        self.system_context = system_context
        self.chat_repo = chat_repo
        self.session_repo = session_repo
    
    async def process_chat_request(self, user: User, request: ChatRequest, jwt_token: str) -> ChatResponse:
        """Process a chat request using the agent with session management."""
        logger.debug(f"Processing chat request for user {user.id}")
        
        # Session ID should always be provided by the frontend
        session_id = request.session_id
        if not isinstance(session_id, str) or not session_id.strip():
            raise ValueError("Session ID is required and cannot be empty or whitespace")
        
        # Verify session belongs to user, create if it doesn't exist
        session = self.session_repo.find_by_user_and_session(user.id, session_id)
        if not session:
            # Auto-create session if it doesn't exist
            logger.info(f"Session {session_id} not found for user {user.id}, creating it")
            alias = request.session_alias or f"Session {session_id.split('_')[-1] if '_' in session_id else session_id}"
            self.session_repo.create(user.id, session_id, alias)
        
        try:
            # Get session info for response
            session = self.session_repo.find_by_user_and_session(user.id, session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Get the agent with session support
            agent = await chat_manager.create_agent(
                user_token=jwt_token,
                user_id=user.id,
                session_id=session_id
            )
            
            response = await agent.ainvoke(
                {
                    "messages": [
                        {"role": "system", "content": self.system_context},
                        {"role": "user", "content": request.content}
                    ],
                },
                config={
                    "configurable": {
                        "thread_id": session_id,
                        "session_id": session_id,
                        "user_id": user.id,
                    }
                }
            )
            
            answer = response["messages"][-1].content
            logger.debug(f"Agent response length: {len(answer)} characters")
            
            return ChatResponse(
                response=answer, 
                session_id=session_id,
                session_alias=session.alias
            )
            
        except Exception as e:
            logger.error(f"Agent invocation failed for user {user.id}: {e}")
            raise AgentInvocationFailedError(user.id, str(e))
    
    async def save_chat_message(self, user_id: int, session_id: str, message: str, response: str) -> None:
        """Save chat message to database with session ID."""
        try:
            chat_message = self.chat_repo.create(
                user_id=user_id,
                session_id=session_id,
                message=message,
                response=response
            )
            logger.debug(f"Saved chat message {chat_message.id} to database for user {user_id}, session {session_id}")
        except Exception as db_error:
            logger.warning(f"Failed to save chat message to database for user {user_id}: {db_error}")
            # Don't fail the request if database save fails
            raise ChatMessageSaveFailedError(user_id, str(db_error))
    
    def get_chat_history(self, user_id: int, session_id: str, limit: int = 50, offset: int = 0) -> ChatHistoryResponse:
        """Get chat history for a specific session (session_id is now required)."""
        logger.debug(f"Retrieving chat history for user {user_id}, session {session_id} (limit: {limit}, offset: {offset})")
        
        # Verify session belongs to user, create if it doesn't exist
        session = self.session_repo.find_by_user_and_session(user_id, session_id)
        if not session:
            # Auto-create session if it doesn't exist
            logger.info(f"Session {session_id} not found for user {user_id}, creating it for history request")
            alias = f"Session {session_id.split('_')[-1] if '_' in session_id else session_id}"
            self.session_repo.create(user_id, session_id, alias)
        
        # Get total count and messages for the specific session
        total_count = self.chat_repo.count_by_user_id_and_session(user_id, session_id)
        messages = self.chat_repo.find_by_user_id_and_session(user_id, session_id, limit=limit, offset=offset)
        
        # Convert to response format
        message_responses = [
            ChatMessageResponse(
                id=msg.id,
                message=msg.user_message,
                response=msg.bot_response or "",
                session_id=msg.session_id,
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
        logger.debug(f"Retrieved {len(message_responses)} chat messages for user {user_id} (total: {total_count})")
        
        # Get the session info for the alias
        session = self.session_repo.find_by_user_and_session(user_id, session_id)
        session_alias = session.alias if session else f"Session {session_id.split('_')[-1] if '_' in session_id else session_id}"
        
        return ChatHistoryResponse(
            messages=message_responses,
            total_count=total_count,
            session_alias=session_alias
        )
    
    def clear_chat_history(self, user_id: int, session_id: str) -> Dict[str, Any]:
        """Clear chat history for a specific session (session_id is now required)."""
        logger.debug(f"Clearing chat history for user {user_id}, session {session_id}")
        
        # Verify session belongs to user, create if it doesn't exist
        session = self.session_repo.find_by_user_and_session(user_id, session_id)
        if not session:
            # Auto-create session if it doesn't exist
            logger.info(f"Session {session_id} not found for user {user_id}, creating it for clear history request")
            alias = f"Session {session_id.split('_')[-1] if '_' in session_id else session_id}"
            self.session_repo.create(user_id, session_id, alias)
        
        deleted_count = self.chat_repo.delete_by_user_id_and_session(user_id, session_id)
        logger.debug(f"Cleared {deleted_count} chat messages for user {user_id}, session {session_id}")
        
        return {
            "message": f"Successfully cleared {deleted_count} chat messages for session {session_id}",
            "deleted_count": deleted_count,
            "session_id": session_id
        }
    
    async def get_user_sessions(self, user_id: int) -> ChatSessionsResponse:
        """Get all chat sessions for a user."""
        logger.debug(f"Retrieving sessions for user {user_id}")
        
        # Get sessions from database with message counts
        sessions_with_counts = self.session_repo.get_sessions_with_message_count(user_id)
        
        # Convert to response format with aliases
        session_info = [
            ChatSessionInfo(
                session_id=session.id,
                alias=session.alias,
                message_count=message_count,
                created_at=session.created_at,
                updated_at=session.updated_at
            )
            for session, message_count in sessions_with_counts
        ]
        
        logger.debug(f"Found {len(session_info)} sessions for user {user_id}")
        
        return ChatSessionsResponse(
            sessions=session_info,
            total_count=len(session_info)
        )
    
    def delete_session(self, user_id: int, session_id: str) -> DeleteSessionResponse:
        """Delete a specific chat session."""
        logger.debug(f"Deleting session {session_id} for user {user_id}")
        
        # Verify session belongs to user
        session = self.session_repo.find_by_user_and_session(user_id, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found for user {user_id}")
        
        # Delete messages from database
        deleted_messages = self.chat_repo.delete_by_user_id_and_session(user_id, session_id)
        
        # Delete the session record
        self.session_repo.delete_by_id(session_id)
        
        logger.debug(f"Deleted session {session_id} and {deleted_messages} messages for user {user_id}")
        
        return DeleteSessionResponse(
            message=f"Successfully deleted session {session_id}",
            session_id=session_id,
            deleted_count=deleted_messages
        )

    async def create_session(self, user_id: int, request: CreateSessionRequest) -> CreateSessionResponse:
        """Create a new chat session."""
        logger.debug(f"Creating new session for user {user_id}")
        
        # Generate session ID
        session_id = chat_manager.generate_session_id(user_id, request.alias)
        
        # Use provided alias or generate one based on current session count
        if request.alias and request.alias.strip():
            alias = request.alias.strip()
        else:
            # Get current session count to generate default alias
            sessions_with_counts = self.session_repo.get_sessions_with_message_count(user_id)
            session_count = len(sessions_with_counts)
            alias = f"Chat #{session_count + 1}"
        
        # Create session in database
        session = self.session_repo.create(user_id, session_id, alias)
        
        logger.debug(f"Created session {session_id} with alias '{alias}' for user {user_id}")
        
        return CreateSessionResponse(
            session_id=session_id,
            alias=alias,
            message="Session created successfully"
        )

    def update_session_alias(self, user_id: int, session_id: str, request: UpdateSessionAliasRequest) -> UpdateSessionAliasResponse:
        """Update session alias."""
        logger.debug(f"Updating alias for session {session_id} of user {user_id}")
        
        # Verify session belongs to user and update alias
        updated_session = self.session_repo.update_alias(user_id, session_id, request.alias)
        if not updated_session:
            raise ValueError(f"Session {session_id} not found for user {user_id}")
        
        logger.debug(f"Updated session {session_id} alias to '{request.alias}' for user {user_id}")
        
        return UpdateSessionAliasResponse(
            session_id=session_id,
            alias=request.alias,
            message="Session alias updated successfully"
        )


def create_chat_service(
    system_context: str = Depends(get_system_context),
    chat_repo: ChatbotMessageRepository = Depends(create_chatbot_message_repository),
    session_repo: ChatSessionRepository = Depends(create_chat_session_repository)
) -> ChatService:
    """Dependency injection function to create ChatService instance."""
    return AgentChatService(system_context, chat_repo, session_repo)
