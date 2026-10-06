from datetime import datetime, timedelta
from backend.app.services.risk_engine import (
    SEVERITY_POINTS,
    get_risk_level,
    calculate_risk_score,
    generate_recommendation
)

class MockEvent:
    def __init__(self, severity: str, timestamp: datetime = None):
        self.severity = severity
        self.timestamp = timestamp or datetime.utcnow()

def test_severity_points_mapping():
    assert SEVERITY_POINTS["INFO"] == 5
    assert SEVERITY_POINTS["LOW"] == 15
    assert SEVERITY_POINTS["MEDIUM"] == 30
    assert SEVERITY_POINTS["HIGH"] == 50
    assert SEVERITY_POINTS["CRITICAL"] == 80

def test_risk_level_thresholds():
    assert get_risk_level(0) == "LOW"
    assert get_risk_level(29) == "LOW"
    assert get_risk_level(30) == "MEDIUM"
    assert get_risk_level(59) == "MEDIUM"
    assert get_risk_level(60) == "HIGH"
    assert get_risk_level(79) == "HIGH"
    assert get_risk_level(80) == "CRITICAL"
    assert get_risk_level(100) == "CRITICAL"

def test_empty_events_risk():
    score, level, breakdown, reasons = calculate_risk_score([])
    assert score == 0
    assert level == "LOW"
    assert "No security events recorded" in reasons[0]

def test_critical_events_escalation():
    now = datetime.utcnow()
    events = [
        MockEvent("CRITICAL", now - timedelta(minutes=10)),
        MockEvent("CRITICAL", now - timedelta(minutes=30)),
        MockEvent("HIGH", now - timedelta(hours=1))
    ]
    score, level, breakdown, reasons = calculate_risk_score(events)
    assert score >= 80
    assert level == "CRITICAL"
    assert breakdown["CRITICAL"] == 2
    assert breakdown["HIGH"] == 1
    assert any("CRITICAL" in r for r in reasons)

def test_low_severity_events():
    now = datetime.utcnow()
    events = [
        MockEvent("INFO", now - timedelta(hours=2)),
        MockEvent("LOW", now - timedelta(hours=4))
    ]
    score, level, breakdown, reasons = calculate_risk_score(events)
    assert score < 30
    assert level == "LOW"
    assert breakdown["INFO"] == 1
    assert breakdown["LOW"] == 1

def test_generate_recommendation():
    rec_critical = generate_recommendation("CRITICAL", "active")
    assert "Immediate isolation" in rec_critical

    rec_high = generate_recommendation("HIGH", "active")
    assert "human approval" in rec_high.lower() or "vigilance" in rec_high.lower()

    rec_low = generate_recommendation("LOW", "active")
    assert "normal" in rec_low.lower()
