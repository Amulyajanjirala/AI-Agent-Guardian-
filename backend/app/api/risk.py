from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..schemas.dashboard import FleetRiskReport
from ..schemas.agent import AgentRiskExplanation
from ..services.agent_service import get_all_agents, get_agent_by_id, get_agent_risk_explanation
from ..services.risk_engine import get_risk_level

router = APIRouter(prefix="/api/risk", tags=["Risk Monitor"])

@router.get("", response_model=FleetRiskReport)
def get_fleet_risk(db: Session = Depends(get_db)):
    """Retrieve aggregate fleet risk metrics and top risk drivers."""
    agents = get_all_agents(db)
    if not agents:
        return {
            "average_risk_score": 0.0,
            "fleet_risk_level": "LOW",
            "total_monitored": 0,
            "risk_breakdown": {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0},
            "top_risk_agents": []
        }

    total_score = sum(a.risk_score for a in agents)
    avg_score = round(total_score / len(agents), 1)
    fleet_level = get_risk_level(int(avg_score))

    breakdown = {
        "LOW": sum(1 for a in agents if a.risk_level == "LOW"),
        "MEDIUM": sum(1 for a in agents if a.risk_level == "MEDIUM"),
        "HIGH": sum(1 for a in agents if a.risk_level == "HIGH"),
        "CRITICAL": sum(1 for a in agents if a.risk_level == "CRITICAL")
    }

    sorted_agents = sorted(agents, key=lambda a: a.risk_score, reverse=True)

    return {
        "average_risk_score": avg_score,
        "fleet_risk_level": fleet_level,
        "total_monitored": len(agents),
        "risk_breakdown": breakdown,
        "top_risk_agents": sorted_agents[:5]
    }

@router.get("/{agent_id}", response_model=AgentRiskExplanation)
def get_agent_risk(agent_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed explainable risk breakdown for an individual agent."""
    agent = get_agent_by_id(agent_id, db)
    return get_agent_risk_explanation(agent, db)
