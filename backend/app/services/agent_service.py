from typing import List, Optional
from sqlalchemy.orm import Session
from ..database.models import Agent, SecurityEvent
from ..core.errors import GuardianAPIException
from ..services.risk_engine import calculate_risk_score, generate_recommendation
from ..schemas.agent import AgentRiskExplanation

def get_all_agents(db: Session) -> List[Agent]:
    """Retrieve all agents with up-to-date risk score calculations."""
    agents = db.query(Agent).all()
    for agent in agents:
        events = db.query(SecurityEvent).filter(SecurityEvent.agent_id == agent.id).all()
        score, level, _, _ = calculate_risk_score(events)
        agent.risk_score = score
        agent.risk_level = level
        agent.recent_events_count = len(events)
    db.commit()
    return agents

def get_agent_by_id(agent_id: str, db: Session) -> Agent:
    """Retrieve a single agent by ID or raise 404."""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise GuardianAPIException(
            code="AGENT_NOT_FOUND",
            message=f"Agent with ID '{agent_id}' does not exist.",
            status_code=404
        )
    return agent

def get_agent_risk_explanation(agent: Agent, db: Session) -> AgentRiskExplanation:
    """Generate detailed risk explanation for an agent."""
    events = db.query(SecurityEvent).filter(SecurityEvent.agent_id == agent.id).order_by(SecurityEvent.timestamp.desc()).all()
    score, level, breakdown, reasons = calculate_risk_score(events)
    recommendation = generate_recommendation(level, agent.status)

    return AgentRiskExplanation(
        agent_id=agent.id,
        agent_name=agent.name,
        risk_score=score,
        risk_level=level,
        event_count_24h=len(events),
        severity_breakdown=breakdown,
        reasons=reasons,
        recommendation=recommendation
    )
