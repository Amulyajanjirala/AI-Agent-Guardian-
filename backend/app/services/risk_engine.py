"""
AI Agent Guardian - Basic Risk Engine (Version 1 Demonstration Model)

Transparent, deterministic risk scoring formula based on:
1. Event severity points (INFO=5, LOW=15, MEDIUM=30, HIGH=50, CRITICAL=80)
2. Event frequency (event accumulation factor)
3. Suspicious activity multipliers (e.g., repeated high/critical incidents)

Scale:
  0 - 29 : LOW
 30 - 59 : MEDIUM
 60 - 79 : HIGH
 80 - 100: CRITICAL
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta

# Severity points defined in specifications
SEVERITY_POINTS: Dict[str, int] = {
    "INFO": 5,
    "LOW": 15,
    "MEDIUM": 30,
    "HIGH": 50,
    "CRITICAL": 80
}

def get_risk_level(score: int) -> str:
    """Categorize numerical risk score (0-100) into defined risk tiers."""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    else:
        return "LOW"

def calculate_risk_score(events: List[Any]) -> Tuple[int, str, Dict[str, int], List[str]]:
    """
    Calculate an agent's risk score from a list of security events.
    Returns:
        (risk_score, risk_level, severity_breakdown, reasons)
    """
    if not events:
        return 0, "LOW", {"INFO": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}, ["No security events recorded. Agent operating within normal parameters."]

    severity_counts = {"INFO": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    reasons: List[str] = []

    total_severity_points = 0
    now = datetime.utcnow()
    recent_events_count = 0

    for ev in events:
        sev = getattr(ev, "severity", "INFO").upper()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            sev = "INFO"
            severity_counts["INFO"] += 1
        
        total_severity_points += SEVERITY_POINTS.get(sev, 5)

        # Check recency (within last 24 hours)
        ts = getattr(ev, "timestamp", now)
        if (now - ts) <= timedelta(hours=24):
            recent_events_count += 1

    # Base score scaled down to 0-60 baseline from raw points
    # E.g. one critical (80 pts) gives ~40 base pts; multiple events escalate
    base_score = min(60, int(total_severity_points * 0.45))

    # Frequency factor (up to 20 points for high event rate)
    frequency_bonus = min(20, recent_events_count * 3)

    # Suspicious pattern multiplier (up to 20 points for critical/high frequency)
    critical_count = severity_counts["CRITICAL"]
    high_count = severity_counts["HIGH"]
    pattern_penalty = 0
    if critical_count > 0:
        pattern_penalty += min(20, critical_count * 12)
    if high_count > 1:
        pattern_penalty += min(10, (high_count - 1) * 5)

    raw_score = base_score + frequency_bonus + pattern_penalty
    final_score = max(0, min(100, raw_score))
    risk_level = get_risk_level(final_score)

    # Generate explainable reasons
    if critical_count > 0:
        reasons.append(f"Detected {critical_count} CRITICAL security violation(s) requiring immediate intervention.")
    if high_count > 0:
        reasons.append(f"Detected {high_count} HIGH severity event(s) indicating potential unauthorized behavior.")
    if severity_counts["MEDIUM"] > 0:
        reasons.append(f"Recorded {severity_counts['MEDIUM']} MEDIUM severity anomaly event(s).")
    if recent_events_count >= 5:
        reasons.append(f"High activity frequency: {recent_events_count} security alerts generated within the last 24 hours.")
    if not reasons:
        reasons.append(f"Minor alerts detected ({severity_counts['LOW']} LOW, {severity_counts['INFO']} INFO). Risk remains constrained.")

    return final_score, risk_level, severity_counts, reasons

def generate_recommendation(risk_level: str, agent_status: str) -> str:
    """Generate operational security guidance based on risk level."""
    if risk_level == "CRITICAL":
        return "Immediate isolation recommended. Quarantine or suspend agent credentials and review tool access logs."
    elif risk_level == "HIGH":
        return "High vigilance recommended. Restrict privileged tool execution and mandate human approval for sensitive actions."
    elif risk_level == "MEDIUM":
        return "Enhanced monitoring recommended. Inspect recent tool calls and observe API frequency patterns."
    else:
        return "Agent is operating normally within acceptable security baselines."
