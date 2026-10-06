from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..database.models import ChatSession, ChatMessage
from ..schemas.chat import ChatRequest, ChatResponse, ChatSessionOut, ChatMessageOut
from ..services.chat_service import process_chat_message

router = APIRouter(prefix="/api/chat", tags=["Guardian Chat"])

@router.post("", response_model=ChatResponse)
def send_chat_message(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Guardian Chat Interface.
    Analyzes user queries, extracts security intent, evaluates real-time agent data,
    and returns conversational responses and structured telemetry cards.
    """
    result = process_chat_message(db, payload.message, payload.session_id)
    return result

@router.get("/sessions", response_model=List[ChatSessionOut])
def get_recent_sessions(limit: int = 10, db: Session = Depends(get_db)):
    """List recent conversation sessions."""
    sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).limit(limit).all()
    return sessions

@router.get("/history/{session_id}", response_model=List[ChatMessageOut])
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    """Retrieve full message history for a specific conversation session."""
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()
    return messages
