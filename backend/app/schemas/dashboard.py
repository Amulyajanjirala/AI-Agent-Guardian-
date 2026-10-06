from pydantic import BaseModel
from typing import List, Dict
from .agent import AgentOut
from .event import SecurityEventOut

class DashboardSummary(BaseModel):
    total_agents: int
    active_agents: int
    security_events_count: int
    high_risk_agents: int
    guardian_status: str = "ONLINE"
    security_status: str = "MONITORING"
    risk_distribution: Dict[str, int]
    recent_alerts: List[SecurityEventOut]
    agents_overview: List[AgentOut]

class FleetRiskReport(BaseModel):
    average_risk_score: float
    fleet_risk_level: str
    total_monitored: int
    risk_breakdown: Dict[str, int]
    top_risk_agents: List[AgentOut]
