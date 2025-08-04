from pydantic import BaseModel
from typing import List
import datetime


class ChatRequest(BaseModel):
    content: str


class ChatResponse(BaseModel):
    response: str


class ChatMessageResponse(BaseModel):
    id: int
    message: str
    response: str
    created_at: datetime.datetime


class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total_count: int
