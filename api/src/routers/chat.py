from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import pickle
from pathlib import Path
from utils import get_current_user

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain.chat_models import init_chat_model

import __main__

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    content: str

class ChatResponse(BaseModel):
    response: str

response_model, retriever_tool = None, None

@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, _ = Depends(get_current_user)):
    try:
        docs = retriever_tool.invoke({"query": request.content})
        full_prompt = f'Contexto:\n{docs}\n\nPregunta del usuario: {request.content}'
        response = response_model.invoke(full_prompt).content
        return ChatResponse(response=response)
    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

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
            "retrieve_flights",
            "Recupera información sobre vuelos según la consulta proporcionada",
        )

        response_model = init_chat_model("openai:gpt-4.1", temperature=0)

    except Exception as e:
        print(f"Error initializing chat: {e}")