from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from repository import User
from schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from resources.dependencies import get_current_user
from resources.logging import get_logger
from services import ChatService, create_chat_service
from exceptions import ApiException
from utils.error_handlers import api_exception_to_http_exception

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()
logger = get_logger("chat_router")

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(create_chat_service)
):
    try:
        logger.debug(f"Processing chat request for user {user.id}")
        
        # Process chat through service
        answer = await chat_service.process_chat_request(user, request)
        
        # Save to database through service
        await chat_service.save_chat_message(user.id, request.content, answer)
        
        logger.info(f"Successfully processed chat request for user {user.email}")
        logger.debug(f"Response length: {len(answer)} characters")
        
        return ChatResponse(response=answer)
        
    except ApiException as e:
        logger.error(f"Error processing chat request for user {user.email}: {e.message}", exc_info=True)
        raise api_exception_to_http_exception(e)
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
    chat_service: ChatService = Depends(create_chat_service)
):
    """
    Get chat history for the current user with pagination.
    """
    try:
        history = chat_service.get_chat_history(user.id, limit=limit, offset=offset)
        
        logger.info(f"Retrieved {len(history.messages)} chat messages for user {user.email} (total: {history.total_count})")
        
        return history
        
    except Exception as e:
        logger.error(f"Error retrieving chat history for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.delete("/history")
def clear_chat_history(
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(create_chat_service)
):
    """
    Clear all chat history for the current user.
    """
    try:
        result = chat_service.clear_chat_history(user.id)
        
        logger.info(f"Cleared {result['deleted_count']} chat messages for user {user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing chat history: {str(e)}"
        )