from typing import List, Optional
from sqlalchemy.orm import Session
from ..database.models import SecurityEvent, Agent
from ..core.errors import GuardianAPIException

def get_security_events(
    db: Session,
    agent_id: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 50
) -> List[dict]:
    """Retrieve security events with optional agent and severity filtering."""
    query = db.query(SecurityEvent, Agent.name.label("agent_name")).outerjoin(
        Agent, SecurityEvent.agent_id == Agent.id
    )

    if agent_id:
        query = query.filter(SecurityEvent.agent_id == agent_id)
    if severity:
        query = query.filter(SecurityEvent.severity == severity.upper())

    results = query.order_by(SecurityEvent.timestamp.desc()).limit(limit).all()

    events_out = []
    for event, agent_name in results:
        event_dict = {
            "id": event.id,
            "agent_id": event.agent_id,
            "agent_name": agent_name or "Unknown Agent",
            "event_type": event.event_type,
            "description": event.description,
            "severity": event.severity,
            "source": event.source,
            "timestamp": event.timestamp
        }
        events_out.append(event_dict)

    return events_out

def get_event_by_id(event_id: str, db: Session) -> dict:
    """Retrieve a single security event by ID."""
    result = db.query(SecurityEvent, Agent.name.label("agent_name")).outerjoin(
        Agent, SecurityEvent.agent_id == Agent.id
    ).filter(SecurityEvent.id == event_id).first()

    if not result:
        raise GuardianAPIException(
            code="EVENT_NOT_FOUND",
            message=f"Security event with ID '{event_id}' does not exist.",
            status_code=404
        )
    event, agent_name = result
    return {
        "id": event.id,
        "agent_id": event.agent_id,
        "agent_name": agent_name or "Unknown Agent",
        "event_type": event.event_type,
        "description": event.description,
        "severity": event.severity,
        "source": event.source,
        "timestamp": event.timestamp
    }
