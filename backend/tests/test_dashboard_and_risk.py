def test_get_dashboard_summary(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["total_agents"] >= 5
    assert data["active_agents"] >= 4
    assert data["security_events_count"] >= 10
    assert data["guardian_status"] == "ONLINE"
    assert data["security_status"] == "MONITORING"
    assert "risk_distribution" in data
    assert len(data["recent_alerts"]) > 0
    assert len(data["agents_overview"]) >= 5

def test_get_fleet_risk(client):
    res = client.get("/api/risk")
    assert res.status_code == 200
    data = res.json()
    assert "average_risk_score" in data
    assert "fleet_risk_level" in data
    assert data["total_monitored"] >= 5
    assert len(data["top_risk_agents"]) > 0

def test_get_individual_agent_risk(client):
    res = client.get("/api/risk/agent-gamma")
    assert res.status_code == 200
    data = res.json()
    assert data["agent_id"] == "agent-gamma"
    assert "reasons" in data
    assert len(data["reasons"]) > 0
    assert "recommendation" in data
