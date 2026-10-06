from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..schemas.dashboard import DashboardSummary
from ..services.agent_service import get_all_agents
from ..services.event_service import get_security_events
from ..database.models import SecurityEvent

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Fetch high-level telemetry, security status, and fleet metrics."""
    agents = get_all_agents(db)
    all_events = db.query(SecurityEvent).all()
    recent_alerts = get_security_events(db, limit=6)

    total_agents = len(agents)
    active_agents = sum(1 for a in agents if a.status == "active")
    high_risk_agents = sum(1 for a in agents if a.risk_level in ["HIGH", "CRITICAL"])

    risk_distribution = {
        "LOW": sum(1 for a in agents if a.risk_level == "LOW"),
        "MEDIUM": sum(1 for a in agents if a.risk_level == "MEDIUM"),
        "HIGH": sum(1 for a in agents if a.risk_level == "HIGH"),
        "CRITICAL": sum(1 for a in agents if a.risk_level == "CRITICAL")
    }

    return {
        "total_agents": total_agents,
        "active_agents": active_agents,
        "security_events_count": len(all_events),
        "high_risk_agents": high_risk_agents,
        "guardian_status": "ONLINE",
        "security_status": "MONITORING",
        "risk_distribution": risk_distribution,
        "recent_alerts": recent_alerts,
        "agents_overview": agents
    }
