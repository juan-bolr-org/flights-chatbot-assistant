from fastapi import APIRouter, Depends, HTTPException, Query, Request
from repository import User
from schemas import ChatRequest, ChatResponse, ChatHistoryResponse, ChatSessionsResponse, DeleteSessionResponse
from resources.dependencies import get_current_user
from resources.logging import get_logger
from services import ChatService, create_chat_service
from exceptions import ApiException
from utils.error_handlers import api_exception_to_http_exception
from typing import Optional

router = APIRouter(prefix="/chat", tags=["chat"])
logger = get_logger("chat_router")

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    req: Request,
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(create_chat_service)
):
    try:
        logger.debug(f"Processing chat request for user {user.id}")
        
        # Get JWT token from request state (set by auth middleware)
        jwt_token = getattr(req.state, 'jwt_token', None)
        if not jwt_token:
            raise HTTPException(status_code=401, detail="No authentication token available")
        
        # Process chat through service (returns ChatResponse with session_id)
        response = await chat_service.process_chat_request(user, request, jwt_token)
        
        # Save to database through service
        await chat_service.save_chat_message(user.id, response.session_id, request.content, response.response)
        
        logger.info(f"Successfully processed chat request for user {user.email}")
        logger.debug(f"Response length: {len(response.response)} characters")
        
        return response
        
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
    session_id: Optional[str] = Query(None, description="Optional session ID to filter history"),
    limit: int = Query(50, ge=1, le=100, description="Number of messages to retrieve"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(create_chat_service)
):
    """
    Get chat history for the current user with optional session filtering and pagination.
    """
    try:
        history = chat_service.get_chat_history(user.id, session_id=session_id, limit=limit, offset=offset)
        
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
    session_id: Optional[str] = Query(None, description="Optional session ID to clear specific session"),
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(create_chat_service)
):
    """
    Clear chat history for the current user, optionally for a specific session.
    """
    try:
        result = chat_service.clear_chat_history(user.id, session_id=session_id)
        
        if session_id:
            logger.info(f"Cleared {result['deleted_count']} chat messages for user {user.email}, session {session_id}")
        else:
            logger.info(f"Cleared {result['deleted_count']} chat messages for user {user.email}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing chat history: {str(e)}"
        )

@router.get("/sessions", response_model=ChatSessionsResponse)
def get_user_sessions(
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(create_chat_service)
):
    """
    Get all chat sessions for the current user.
    """
    try:
        sessions = chat_service.get_user_sessions(user.id)
        
        logger.info(f"Retrieved {sessions.total_count} sessions for user {user.email}")
        
        return sessions
        
    except Exception as e:
        logger.error(f"Error retrieving sessions for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving sessions: {str(e)}"
        )

@router.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
def delete_session(
    session_id: str,
    user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(create_chat_service)
):
    """
    Delete a specific chat session for the current user.
    """
    try:
        result = chat_service.delete_session(user.id, session_id)
        
        logger.info(f"Deleted session {session_id} for user {user.email} ({result.deleted_count} messages)")
        
        return result
        
    except Exception as e:
        logger.error(f"Error deleting session {session_id} for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting session: {str(e)}"
        )