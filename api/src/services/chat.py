from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from fastapi import Depends, Request
from repository import User
from schemas import ChatRequest, ChatResponse, ChatHistoryResponse, ChatSessionsResponse, DeleteSessionResponse, ChatMessageResponse
from resources.dependencies import get_system_context
from repository import ChatbotMessageRepository, create_chatbot_message_repository
from resources.logging import get_logger
from resources.chat import chat_manager
from exceptions import AgentInvocationFailedError, ChatMessageSaveFailedError
import uuid

logger = get_logger("chat_service")


class ChatService(ABC):
    """Abstract base class for Chat service operations."""
    
    @abstractmethod
    async def process_chat_request(self, user: User, request: ChatRequest, jwt_token: str) -> ChatResponse:
        """Process a chat request and return the response with session ID."""
        pass
    
    @abstractmethod
    async def save_chat_message(self, user_id: int, session_id: str, message: str, response: str) -> None:
        """Save chat message to database with session ID."""
        pass
    
    @abstractmethod
    def get_chat_history(self, user_id: int, session_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> ChatHistoryResponse:
        """Get chat history for a user with optional session filtering and pagination."""
        pass
    
    @abstractmethod
    def clear_chat_history(self, user_id: int, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear chat history for a user, optionally for a specific session."""
        pass
    
    @abstractmethod
    async def get_user_sessions(self, user_id: int) -> ChatSessionsResponse:
        """Get all chat sessions for a user."""
        pass
    
    @abstractmethod
    def delete_session(self, user_id: int, session_id: str) -> DeleteSessionResponse:
        """Delete a specific chat session for a user."""
        pass


class AgentChatService(ChatService):
    """Implementation of ChatService using LangChain agent with session support."""
    
    def __init__(self, system_context: str, chat_repo: ChatbotMessageRepository):
        self.system_context = system_context
        self.chat_repo = chat_repo
    
    async def process_chat_request(self, user: User, request: ChatRequest, jwt_token: str) -> ChatResponse:
        """Process a chat request using the agent with session management."""
        logger.debug(f"Processing chat request for user {user.id}")
        
        session_id = chat_manager.generate_session_id(user.id, request.session_id)
        
        try:
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
            
            return ChatResponse(response=answer, session_id=session_id)
            
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
    
    def get_chat_history(self, user_id: int, session_id: Optional[str] = None, limit: int = 50, offset: int = 0) -> ChatHistoryResponse:
        """Get chat history for a user with optional session filtering and pagination."""
        logger.debug(f"Retrieving chat history for user {user_id}, session {session_id} (limit: {limit}, offset: {offset})")
        
        # Get total count
        if session_id:
            total_count = self.chat_repo.count_by_user_id_and_session(user_id, session_id)
            messages = self.chat_repo.find_by_user_id_and_session(user_id, session_id, limit=limit, offset=offset)
        else:
            total_count = self.chat_repo.count_by_user_id(user_id)
            messages = self.chat_repo.find_by_user_id(user_id, limit=limit, offset=offset)
        
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
        
        return ChatHistoryResponse(
            messages=message_responses,
            total_count=total_count
        )
    
    def clear_chat_history(self, user_id: int, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear chat history for a user, optionally for a specific session."""
        if session_id:
            logger.debug(f"Clearing chat history for user {user_id}, session {session_id}")
            deleted_count = self.chat_repo.delete_by_user_id_and_session(user_id, session_id)
            logger.debug(f"Cleared {deleted_count} chat messages for user {user_id}, session {session_id}")
            return {
                "message": f"Successfully cleared {deleted_count} chat messages for session {session_id}",
                "deleted_count": deleted_count,
                "session_id": session_id
            }
        else:
            logger.debug(f"Clearing all chat history for user {user_id}")
            deleted_count = self.chat_repo.delete_by_user_id(user_id)
            logger.debug(f"Cleared {deleted_count} chat messages for user {user_id}")
            return {
                "message": f"Successfully cleared {deleted_count} chat messages",
                "deleted_count": deleted_count
            }
    
    async def get_user_sessions(self, user_id: int) -> ChatSessionsResponse:
        """Get all chat sessions for a user."""
        logger.debug(f"Retrieving sessions for user {user_id}")
        
        # Get sessions from database
        db_sessions = self.chat_repo.get_user_sessions(user_id)
        
        # Get sessions from checkpointer
        checkpoint_sessions = await chat_manager.get_user_sessions(user_id)
        
        # Combine and deduplicate
        all_sessions = list(set(db_sessions + checkpoint_sessions))
        
        logger.debug(f"Found {len(all_sessions)} sessions for user {user_id}")
        
        return ChatSessionsResponse(
            sessions=all_sessions,
            total_count=len(all_sessions)
        )
    
    def delete_session(self, user_id: int, session_id: str) -> DeleteSessionResponse:
        """Delete a specific chat session for a user."""
        logger.debug(f"Deleting session {session_id} for user {user_id}")
        
        # Delete from database
        deleted_count = self.chat_repo.delete_by_user_id_and_session(user_id, session_id)
        
        # Note: We don't delete from the checkpointer as it may contain useful state
        # The checkpointer will naturally expire old sessions based on its configuration
        
        logger.debug(f"Deleted {deleted_count} chat messages for user {user_id}, session {session_id}")
        
        return DeleteSessionResponse(
            message=f"Successfully deleted session {session_id}",
            session_id=session_id,
            deleted_count=deleted_count
        )


def create_chat_service(
    system_context: str = Depends(get_system_context),
    chat_repo: ChatbotMessageRepository = Depends(create_chatbot_message_repository)
) -> ChatService:
    """Dependency injection function to create ChatService instance."""
    return AgentChatService(system_context, chat_repo)
