from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from .event import SecurityEventOut

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "active"
    agent_type: str = "general"

class AgentCreate(AgentBase):
    id: str

class AgentOut(AgentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    risk_score: int
    risk_level: str
    created_at: datetime
    last_activity: datetime
    recent_events_count: Optional[int] = 0

class AgentRiskExplanation(BaseModel):
    agent_id: str
    agent_name: str
    risk_score: int
    risk_level: str
    event_count_24h: int
    severity_breakdown: dict
    reasons: List[str]
    recommendation: str

class AgentDetail(AgentOut):
    events: List[SecurityEventOut] = []
    risk_explanation: Optional[AgentRiskExplanation] = None
