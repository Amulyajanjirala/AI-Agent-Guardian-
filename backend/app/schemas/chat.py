from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any, List, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    data: List[Any] = []
    session_id: str

class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sender: str
    message: str
    intent: Optional[str] = None
    timestamp: datetime
    metadata_json: Optional[str] = None

class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    messages: List[ChatMessageOut] = []
