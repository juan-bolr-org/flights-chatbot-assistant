from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from models import User
import os
from resources.dependencies import get_current_user, get_chat_model, get_chat_memory, get_faq_tool, get_system_context
from utils.chatbot_tools import create_chatbot_tools
from langchain.chat_models.base import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from resources.logging import get_logger

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()
logger = get_logger("chat_router")


class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str

api_base_port = os.getenv("PORT", "8000")

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    chat_model: BaseChatModel = Depends(get_chat_model),
    memory: MemorySaver = Depends(get_chat_memory),
    faq_tool = Depends(get_faq_tool),
    system_context: str = Depends(get_system_context)
):
    try:
        user_token = credentials.credentials
        
        logger.debug(f"Creating chatbot tools for user {user.id}")
        chatbot_tools = create_chatbot_tools(
            user_token=user_token,
            user_id=user.id,
            api_base_url=f"http://localhost:{api_base_port}",
        )
        
        # Add FAQ tool if available
        if faq_tool is not None:
            chatbot_tools = chatbot_tools + [faq_tool]
            logger.debug("Added FAQ tool to chatbot tools")
        else:
            logger.warning("No FAQ tool available, skipping...")

        logger.debug("Creating react agent...")
        agent = create_react_agent(
            tools=chatbot_tools,
            model=chat_model,
            checkpointer=memory
        )
        
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