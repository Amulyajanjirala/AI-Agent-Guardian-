import json
import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..database.models import Agent, SecurityEvent, ChatSession, ChatMessage
from ..services.risk_engine import calculate_risk_score, generate_recommendation

def detect_intent(message: str) -> str:
    """Identify security intent using pattern matching."""
    msg = message.lower().strip()

    agent_names = ["alpha", "beta", "gamma", "delta", "epsilon"]
    has_agent = any(name in msg for name in agent_names)

    # 1. Highest risk across fleet
    if any(q in msg for q in ["highest risk", "most risky", "most vulnerable", "highest threat"]) and not has_agent:
        return "GET_HIGHEST_RISK_AGENT"

    # 2. Specific agent risk / status inquiry
    if has_agent or any(q in msg for q in ["why is", "risk for", "behaving normally", "status of agent", "how is agent"]):
        return "GET_AGENT_RISK"

    # 3. Fleet-wide high risk query
    if any(q in msg for q in ["high risk", "critical agent", "dangerous agent", "elevated risk"]):
        return "GET_HIGH_RISK_AGENTS"

    # 4. Security events inquiry
    if any(q in msg for q in ["event", "alerts", "incident", "logs", "suspicious", "what happened"]):
        return "GET_SECURITY_EVENTS"

    # 5. Security summary
    if any(q in msg for q in ["summary", "overview", "what's happening", "whats happening", "fleet status", "posture"]):
        return "GET_SECURITY_SUMMARY"

    # 6. List all agents
    if any(q in msg for q in ["agents", "list agents", "show agents", "all agents", "registered agents"]):
        return "GET_AGENTS"

    return "UNKNOWN"

def extract_agent_target(message: str, agents: List[Agent]) -> Optional[Agent]:
    """Extract which agent the user is asking about."""
    msg = message.lower()
    for agent in agents:
        if agent.name.lower() in msg or agent.id.lower() in msg:
            return agent
    # Check simple names
    for name in ["alpha", "beta", "gamma", "delta", "epsilon"]:
        if name in msg:
            for agent in agents:
                if name in agent.id.lower() or name in agent.name.lower():
                    return agent
    return None

def process_chat_message(db: Session, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """Process incoming chat message, identify intent, query DB, and record chat history."""
    if not session_id:
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        session = ChatSession(id=session_id, title=message[:50])
        db.add(session)
        db.commit()
    else:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(id=session_id, title=message[:50])
            db.add(session)
            db.commit()

    # Record user message
    user_msg_id = f"msg-{uuid.uuid4().hex[:8]}"
    user_msg = ChatMessage(
        id=user_msg_id,
        session_id=session_id,
        sender="user",
        message=message,
        timestamp=datetime.utcnow()
    )
    db.add(user_msg)

    # Detect intent
    intent = detect_intent(message)
    agents = db.query(Agent).all()
    events = db.query(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).all()

    response_text = ""
    data_payload: List[Dict[str, Any]] = []

    if intent == "GET_HIGH_RISK_AGENTS":
        high_risk = []
        for a in agents:
            ag_events = [e for e in events if e.agent_id == a.id]
            score, level, _, _ = calculate_risk_score(ag_events)
            if level in ["HIGH", "CRITICAL"]:
                high_risk.append({
                    "id": a.id,
                    "name": a.name,
                    "status": a.status,
                    "risk_score": score,
                    "risk_level": level,
                    "agent_type": a.agent_type
                })
        
        count = len(high_risk)
        if count == 0:
            response_text = "Good news: No high-risk or critical agents are currently detected in the fleet."
        else:
            response_text = f"{count} high-risk agent{'s were' if count > 1 else ' was'} detected requiring administrative attention."
        data_payload = high_risk

    elif intent == "GET_HIGHEST_RISK_AGENT":
        scored_agents = []
        for a in agents:
            ag_events = [e for e in events if e.agent_id == a.id]
            score, level, breakdown, reasons = calculate_risk_score(ag_events)
            scored_agents.append((score, level, a, breakdown, reasons))
        
        if scored_agents:
            scored_agents.sort(key=lambda x: x[0], reverse=True)
            top_score, top_level, top_agent, top_breakdown, top_reasons = scored_agents[0]
            response_text = f"{top_agent.name} currently has the highest risk score at {top_score}/100 ({top_level})."
            data_payload = [{
                "id": top_agent.id,
                "name": top_agent.name,
                "risk_score": top_score,
                "risk_level": top_level,
                "status": top_agent.status,
                "reasons": top_reasons
            }]
        else:
            response_text = "No registered agents found to evaluate."

    elif intent == "GET_AGENT_RISK":
        target = extract_agent_target(message, agents)
        if target:
            ag_events = [e for e in events if e.agent_id == target.id]
            score, level, breakdown, reasons = calculate_risk_score(ag_events)
            recommendation = generate_recommendation(level, target.status)

            if "normally" in message.lower():
                if level == "LOW":
                    response_text = f"{target.name} is behaving normally. Current risk level is LOW ({score}/100) with no anomalous patterns."
                else:
                    response_text = f"{target.name} is NOT operating within normal baselines. Current risk level: {level} ({score}/100) due to flagged activities."
            else:
                response_text = f"{target.name} currently has a risk score of {score}/100 ({level}). Primary reason: {reasons[0] if reasons else 'Normal behavior'}"

            data_payload = [{
                "id": target.id,
                "name": target.name,
                "status": target.status,
                "risk_score": score,
                "risk_level": level,
                "reasons": reasons,
                "severity_breakdown": breakdown,
                "recommendation": recommendation,
                "recent_event_count": len(ag_events)
            }]
        else:
            response_text = "Please specify which agent you would like to inspect (e.g., Agent Alpha, Agent Beta, Agent Gamma)."

    elif intent == "GET_SECURITY_EVENTS":
        recent = events[:8]
        response_text = f"Found {len(events)} total security events across the agent fleet. Showing the 8 most recent alerts."
        data_payload = [
            {
                "id": e.id,
                "agent_id": e.agent_id,
                "event_type": e.event_type,
                "description": e.description,
                "severity": e.severity,
                "source": e.source,
                "timestamp": e.timestamp.isoformat()
            }
            for e in recent
        ]

    elif intent == "GET_SECURITY_SUMMARY":
        total_agents = len(agents)
        active_agents = sum(1 for a in agents if a.status == "active")
        suspended_agents = sum(1 for a in agents if a.status == "suspended")
        high_severity_events = sum(1 for e in events if e.severity in ["HIGH", "CRITICAL"])
        
        response_text = (
            f"I am monitoring {total_agents} registered agents. {active_agents} are active and {suspended_agents} are suspended. "
            f"There are {len(events)} security events recorded, including {high_severity_events} elevated alerts. "
            f"Guardian Status: ONLINE | Security Status: MONITORING."
        )
        data_payload = [{
            "total_agents": total_agents,
            "active_agents": active_agents,
            "suspended_agents": suspended_agents,
            "total_events": len(events),
            "elevated_events": high_severity_events,
            "guardian_status": "ONLINE",
            "security_status": "MONITORING"
        }]

    elif intent == "GET_AGENTS":
        agents_data = []
        for a in agents:
            ag_events = [e for e in events if e.agent_id == a.id]
            score, level, _, _ = calculate_risk_score(ag_events)
            agents_data.append({
                "id": a.id,
                "name": a.name,
                "status": a.status,
                "agent_type": a.agent_type,
                "risk_score": score,
                "risk_level": level
            })
        response_text = f"Retrieved {len(agents)} registered AI agents under Guardian surveillance."
        data_payload = agents_data

    else:
        # UNKNOWN intent fallback
        response_text = (
            "I am the Guardian AI Security Assistant. I can help monitor your AI agents, "
            "inspect suspicious tool calls, calculate risk scores, and investigate security events."
        )
        data_payload = [
            {"suggestion": "Show me high-risk agents"},
            {"suggestion": "Why is Agent Gamma high risk?"},
            {"suggestion": "What security events happened recently?"},
            {"suggestion": "Give me today's security summary"},
            {"suggestion": "Is Agent Alpha behaving normally?"}
        ]

    # Store assistant response in history
    guardian_msg_id = f"msg-{uuid.uuid4().hex[:8]}"
    guardian_msg = ChatMessage(
        id=guardian_msg_id,
        session_id=session_id,
        sender="guardian",
        message=response_text,
        intent=intent,
        metadata_json=json.dumps(data_payload),
        timestamp=datetime.utcnow()
    )
    db.add(guardian_msg)
    db.commit()

    return {
        "response": response_text,
        "intent": intent,
        "data": data_payload,
        "session_id": session_id
    }
