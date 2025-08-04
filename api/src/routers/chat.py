from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from models import User
from resources.dependencies import get_current_user, get_agent, get_system_context
from resources.logging import get_logger

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()
logger = get_logger("chat_router")


class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    user: User = Depends(get_current_user),
    agent = Depends(get_agent),
    system_context: str = Depends(get_system_context)
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
        logger.info(f"Successfully processed chat request for user {user.email}")
        logger.debug(f"Response length: {len(answer)} characters")
        
        return ChatResponse(response=answer)
        
    except Exception as e:
        logger.error(f"Error processing chat request for user {user.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat request: {str(e)}"
        )