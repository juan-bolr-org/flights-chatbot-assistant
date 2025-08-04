from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from models import User, ChatbotMessage
from schemas import ChatRequest, ChatResponse, ChatMessageResponse, ChatHistoryResponse
from resources.dependencies import get_current_user, get_agent, get_system_context, get_database_session
from resources.logging import get_logger
import datetime

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()
logger = get_logger("chat_router")

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    user: User = Depends(get_current_user),
    agent = Depends(get_agent),
    system_context: str = Depends(get_system_context),
    db: Session = Depends(get_database_session)
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
            chat_message = ChatbotMessage(
                user_id=user.id,
                message=request.content,
                response=answer,
                created_at=datetime.datetime.now(datetime.UTC)
            )
            db.add(chat_message)
            db.commit()
            db.refresh(chat_message)
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
    db: Session = Depends(get_database_session)
):
    """
    Get chat history for the current user with pagination.
    """
    try:
        logger.debug(f"Retrieving chat history for user {user.id} (limit: {limit}, offset: {offset})")
        
        # Get total count
        total_count = db.query(ChatbotMessage).filter(ChatbotMessage.user_id == user.id).count()
        
        # Get messages with pagination, ordered by most recent first
        messages = db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user.id
        ).order_by(
            ChatbotMessage.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Convert to response format
        message_responses = [
            ChatMessageResponse(
                id=msg.id,
                message=msg.message,
                response=msg.response or "",
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
    db: Session = Depends(get_database_session)
):
    """
    Clear all chat history for the current user.
    """
    try:
        logger.debug(f"Clearing chat history for user {user.id}")
        
        # Count messages before deletion for logging
        message_count = db.query(ChatbotMessage).filter(ChatbotMessage.user_id == user.id).count()
        
        # Delete all chat messages for the user
        deleted_count = db.query(ChatbotMessage).filter(
            ChatbotMessage.user_id == user.id
        ).delete()
        
        db.commit()
        
        logger.info(f"Cleared {deleted_count} chat messages for user {user.email}")
        
        return {
            "message": f"Successfully cleared {deleted_count} chat messages",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing chat history for user {user.email}: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing chat history: {str(e)}"
        )