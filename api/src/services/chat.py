from abc import ABC, abstractmethod
from typing import Dict, Any
from fastapi import Depends
from repository import User
from schemas import ChatRequest, ChatMessageResponse, ChatHistoryResponse
from resources.dependencies import get_agent, get_system_context
from repository import ChatbotMessageRepository, create_chatbot_message_repository
from resources.logging import get_logger
from exceptions import AgentInvocationFailedError, ChatMessageSaveFailedError

logger = get_logger("chat_service")


class ChatService(ABC):
    """Abstract base class for Chat service operations."""
    
    @abstractmethod
    async def process_chat_request(self, user: User, request: ChatRequest) -> str:
        """Process a chat request and return the response."""
        pass
    
    @abstractmethod
    async def save_chat_message(self, user_id: int, message: str, response: str) -> None:
        """Save chat message to database."""
        pass
    
    @abstractmethod
    def get_chat_history(self, user_id: int, limit: int = 50, offset: int = 0) -> ChatHistoryResponse:
        """Get chat history for a user with pagination."""
        pass
    
    @abstractmethod
    def clear_chat_history(self, user_id: int) -> Dict[str, Any]:
        """Clear all chat history for a user."""
        pass


class AgentChatService(ChatService):
    """Implementation of ChatService using LangChain agent."""
    
    def __init__(self, agent, system_context: str, chat_repo: ChatbotMessageRepository):
        self.agent = agent
        self.system_context = system_context
        self.chat_repo = chat_repo
    
    async def process_chat_request(self, user: User, request: ChatRequest) -> str:
        """Process a chat request using the agent."""
        logger.debug(f"Processing chat request for user {user.id}")
        
        try:
            response = await self.agent.ainvoke(
                {
                    "messages": [
                        {"role": "system", "content": self.system_context},
                        {"role": "user", "content": request.content}
                    ],
                },
                config={
                    "configurable": {
                        "session_id": f"chat_session_{user.id}", 
                        "thread_id": f"chat_thread_{user.id}"
                    }
                }
            )
            
            answer = response["messages"][-1].content
            logger.debug(f"Agent response length: {len(answer)} characters")
            
            return answer
        except Exception as e:
            logger.error(f"Agent invocation failed for user {user.id}: {e}")
            raise AgentInvocationFailedError(user.id, str(e))
    
    async def save_chat_message(self, user_id: int, message: str, response: str) -> None:
        """Save chat message to database."""
        try:
            chat_message = self.chat_repo.create(
                user_id=user_id,
                message=message,
                response=response
            )
            logger.debug(f"Saved chat message {chat_message.id} to database for user {user_id}")
        except Exception as db_error:
            logger.warning(f"Failed to save chat message to database for user {user_id}: {db_error}")
            # Don't fail the request if database save fails
            raise ChatMessageSaveFailedError(user_id, str(db_error))
    
    def get_chat_history(self, user_id: int, limit: int = 50, offset: int = 0) -> ChatHistoryResponse:
        """Get chat history for a user with pagination."""
        logger.debug(f"Retrieving chat history for user {user_id} (limit: {limit}, offset: {offset})")
        
        # Get total count
        total_count = self.chat_repo.count_by_user_id(user_id)
        
        # Get messages with pagination, ordered by most recent first
        messages = self.chat_repo.find_by_user_id(user_id, limit=limit, offset=offset)
        
        # Convert to response format
        message_responses = [
            ChatMessageResponse(
                id=msg.id,
                message=msg.user_message,
                response=msg.bot_response or "",
                created_at=msg.created_at
            )
            for msg in messages
        ]
        
        logger.debug(f"Retrieved {len(message_responses)} chat messages for user {user_id} (total: {total_count})")
        
        return ChatHistoryResponse(
            messages=message_responses,
            total_count=total_count
        )
    
    def clear_chat_history(self, user_id: int) -> Dict[str, Any]:
        """Clear all chat history for a user."""
        logger.debug(f"Clearing chat history for user {user_id}")
        
        # Delete all chat messages for the user
        deleted_count = self.chat_repo.delete_by_user_id(user_id)
        
        logger.debug(f"Cleared {deleted_count} chat messages for user {user_id}")
        
        return {
            "message": f"Successfully cleared {deleted_count} chat messages",
            "deleted_count": deleted_count
        }


def create_chat_service(
    agent = Depends(get_agent),
    system_context: str = Depends(get_system_context),
    chat_repo: ChatbotMessageRepository = Depends(create_chatbot_message_repository)
) -> ChatService:
    """Dependency injection function to create ChatService instance."""
    return AgentChatService(agent, system_context, chat_repo)
