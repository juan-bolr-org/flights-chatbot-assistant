from pydantic import BaseModel
from typing import List, Optional
import datetime


class ChatRequest(BaseModel):
    content: str
    session_id: str  # Required session ID
    session_alias: Optional[str] = None  # Allow users to specify session alias for new sessions


class ChatResponse(BaseModel):
    response: str
    session_id: str  # Return the session ID used
    session_alias: str  # Return the session alias


class ChatSessionInfo(BaseModel):
    session_id: str
    alias: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    message_count: int


class ChatMessageResponse(BaseModel):
    id: int
    message: str
    response: str
    session_id: str
    created_at: datetime.datetime


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total_count: int
    session_alias: str


class ChatSessionsResponse(BaseModel):
    sessions: List[ChatSessionInfo]
    total_count: int


class CreateSessionRequest(BaseModel):
    alias: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    alias: str
    message: str


class UpdateSessionAliasRequest(BaseModel):
    alias: str


class UpdateSessionAliasResponse(BaseModel):
    session_id: str
    alias: str
    message: str


class DeleteSessionResponse(BaseModel):
    message: str
    session_id: str
    deleted_count: int
