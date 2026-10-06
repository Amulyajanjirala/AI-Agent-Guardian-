from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database.database import get_db
from ..schemas.event import SecurityEventOut
from ..services.event_service import get_security_events, get_event_by_id

router = APIRouter(prefix="/api/events", tags=["Security Events"])

@router.get("", response_model=List[SecurityEventOut])
def list_events(
    agent_id: Optional[str] = Query(None, description="Filter by agent identifier"),
    severity: Optional[str] = Query(None, description="Filter by severity: INFO, LOW, MEDIUM, HIGH, CRITICAL"),
    limit: int = Query(50, ge=1, le=100, description="Max events to return"),
    db: Session = Depends(get_db)
):
    """Retrieve security events with optional agent or severity filters."""
    return get_security_events(db, agent_id=agent_id, severity=severity, limit=limit)

@router.get("/{event_id}", response_model=SecurityEventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    """Retrieve an individual security event by ID."""
    return get_event_by_id(event_id, db)
