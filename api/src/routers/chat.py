from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import pickle
import os
from pathlib import Path
from utils import get_current_user
from utils.chatbot_tools import create_chatbot_tools

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()


class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str

response_model, retriever_tool = None, None

def init_chat():
    """Initialize the chat model and retriever tool."""
    global response_model, retriever_tool
    print("Initializing chat model and retriever tool...")
    try:   
        # Load flight_docs.pkl from chatbot folder TODO: Fix path of the model
        flight_docs_path = Path(__file__).parent.parent.parent / "flight_docs.pkl"
        with open(flight_docs_path, "rb") as f:
            flight_splits = pickle.load(f)

        vectorstore = InMemoryVectorStore.from_documents(
            documents=flight_splits, embedding=OpenAIEmbeddings()
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 30})

        retriever_tool = create_retriever_tool(
            retriever,
            "retrieve_flight_docs",
            "Search through flight documentation and FAQ information. Use this for general flight policies, procedures, baggage rules, check-in information, and other flight-related documentation that users might ask about.",
        )

        response_model = init_chat_model("openai:gpt-4.1", temperature=0)

    except Exception as e:
        print(f"Error initializing chat: {e}")



@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, 
    user = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        # Get the user's token for API calls
        user_token = credentials.credentials
        
        # Get API base Port from environment or use default
        api_base_port = os.getenv("PORT", "8000")
        
        # Create chatbot tools with user context
        chatbot_tools = create_chatbot_tools(
            user_token=user_token,
            user_id=user.id,
            api_base_url=f"http://localhost:{api_base_port}",
        )
        
        # Add the retriever tool to the list - putting it first so it's prioritized for general FAQ/documentation queries
        all_tools = chatbot_tools
        
        # Create the agent with all tools
        agent = create_react_agent(
            tools=all_tools,
            model=response_model,
            verbose=True,
        )
        
        # Create a system message to help the agent understand when to use each tool
        system_context = """
        You are a helpful flight booking assistant. You have access to several tools:
        
        1. retrieve_flight_docs: Use this for general flight information, policies, FAQ, baggage rules, check-in procedures, etc.
        2. search_flights: Use this to search for available flights based on specific criteria
        3. list_all_flights: Use this to show all available flights
        4. book_flight: Use this to make flight reservations
        5. get_my_bookings: Use this to show user's current bookings
        6. cancel_booking: Use this to cancel existing bookings
        
        Always be helpful and provide accurate information. If you need to search for flights or manage bookings, use the appropriate API tools. For general questions about flight policies or procedures, use the document retriever tool.
        """
        
        # Invoke the agent with the user's message and system context
        response = await agent.ainvoke({
            "messages": [
                {"role": "system", "content": system_context},
                {"role": "user", "content": request.content}
            ]
        })

        for message in response["messages"]:
            print(message.content)
        
        # Extract the final response
        answer = response["messages"][-1].content
        
        return ChatResponse(response=answer)
    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")