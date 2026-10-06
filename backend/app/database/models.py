import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    role = Column(String(20), default="admin", nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    chat_sessions = relationship("ChatSession", back_populates="user")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active", nullable=False)  # active, suspended, idle
    agent_type = Column(String(50), default="general", nullable=False)
    risk_score = Column(Integer, default=0, nullable=False)
    risk_level = Column(String(20), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.datetime.utcnow)

    events = relationship("SecurityEvent", back_populates="agent", cascade="all, delete-orphan")

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(String(50), primary_key=True, index=True)
    agent_id = Column(String(50), ForeignKey("agents.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    source = Column(String(50), default="tool_monitor", nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    agent = relationship("Agent", back_populates="events")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(200), default="New Security Chat")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(50), primary_key=True, index=True)
    session_id = Column(String(50), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # user, guardian
    message = Column(Text, nullable=False)
    intent = Column(String(50), nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON-encoded string for attached structured data
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
