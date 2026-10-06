from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..schemas.agent import AgentOut, AgentDetail
from ..services.agent_service import get_all_agents, get_agent_by_id, get_agent_risk_explanation
from ..services.event_service import get_security_events

router = APIRouter(prefix="/api/agents", tags=["Agents"])

@router.get("", response_model=List[AgentOut])
def list_agents(db: Session = Depends(get_db)):
    """List all registered AI agents under monitoring with risk scores."""
    return get_all_agents(db)

@router.get("/{agent_id}", response_model=AgentDetail)
def get_agent_detail(agent_id: str, db: Session = Depends(get_db)):
    """Get full details for an agent including risk explanation and recent security events."""
    agent = get_agent_by_id(agent_id, db)
    events = get_security_events(db, agent_id=agent.id, limit=20)
    explanation = get_agent_risk_explanation(agent, db)

    return {
        "id": agent.id,
        "name": agent.name,
        "description": agent.description,
        "status": agent.status,
        "agent_type": agent.agent_type,
        "risk_score": explanation.risk_score,
        "risk_level": explanation.risk_level,
        "created_at": agent.created_at,
        "last_activity": agent.last_activity,
        "recent_events_count": len(events),
        "events": events,
        "risk_explanation": explanation
    }
