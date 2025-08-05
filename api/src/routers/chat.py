from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from repository.user import User
from schemas import ChatRequest, ChatResponse, ChatMessageResponse, ChatHistoryResponse
from resources.dependencies import get_current_user, get_agent, get_system_context
from resources.logging import get_logger
from repository import ChatbotMessageRepository, create_chatbot_message_repository

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()
logger = get_logger("chat_router")

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    user: User = Depends(get_current_user),
    agent = Depends(get_agent),
    system_context: str = Depends(get_system_context),
    chat_repo: ChatbotMessageRepository = Depends(create_chatbot_message_repository)
):
    try:
        logger.debug(f"Invoking agent for user {user.id}")
        response = await agent.ainvoke(
            {
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": request.content}
                ],
            },
            config={"configurable": {"session_id": f"chat_session_{user.id}", "thread_id": f"chat_thread_{user.id}"}}
        )
        
        answer = response["messages"][-1].content
        
        # Save the chat message to database
        try:
            chat_message = chat_repo.create(
                user_id=user.id,
                message=request.content,
                response=answer
            )
            logger.debug(f"Saved chat message {chat_message.id} to database for user {user.id}")
        except Exception as db_error:
            logger.warning(f"Failed to save chat message to database for user {user.email}: {db_error}")
            # Don't fail the request if database save fails
        
        logger.info(f"Successfully processed chat request for user {user.email}")
        logger.debug(f"Response length: {len(answer)} characters")
        
        return ChatResponse(response=answer)
        
    except Exception as e:
        logger.error(f"Error processing chat request for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/history", response_model=ChatHistoryResponse)
def get_chat_history(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    chat_repo: ChatbotMessageRepository = Depends(create_chatbot_message_repository)
):
    """
    Get chat history for the current user with pagination.
    """
    try:
        logger.debug(f"Retrieving chat history for user {user.id} (limit: {limit}, offset: {offset})")
        
        # Get total count
        total_count = chat_repo.count_by_user_id(user.id)
        
        # Get messages with pagination, ordered by most recent first
        messages = chat_repo.find_by_user_id(user.id, limit=limit, offset=offset)
        
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
        
        logger.info(f"Retrieved {len(message_responses)} chat messages for user {user.email} (total: {total_count})")
        
        return ChatHistoryResponse(
            messages=message_responses,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"Error retrieving chat history for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.delete("/history")
def clear_chat_history(
    user: User = Depends(get_current_user),
    chat_repo: ChatbotMessageRepository = Depends(create_chatbot_message_repository)
):
    """
    Clear all chat history for the current user.
    """
    try:
        logger.debug(f"Clearing chat history for user {user.id}")
        
        # Delete all chat messages for the user
        deleted_count = chat_repo.delete_by_user_id(user.id)
        
        logger.info(f"Cleared {deleted_count} chat messages for user {user.email}")
        
        return {
            "message": f"Successfully cleared {deleted_count} chat messages",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing chat history: {str(e)}"
        )