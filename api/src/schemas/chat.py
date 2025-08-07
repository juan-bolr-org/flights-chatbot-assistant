from pydantic import BaseModel
from typing import List, Optional
import datetime


class ChatRequest(BaseModel):
    content: str
    session_id: Optional[str] = None  # Allow users to specify session ID


class ChatResponse(BaseModel):
    response: str
    session_id: str  # Return the session ID used


class ChatMessageResponse(BaseModel):
    id: int
    message: str
    response: str
    session_id: str
    created_at: datetime.datetime


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total_count: int


class ChatSessionsResponse(BaseModel):
    sessions: List[str]
    total_count: int


class DeleteSessionResponse(BaseModel):
    message: str
    session_id: str
    deleted_count: int
