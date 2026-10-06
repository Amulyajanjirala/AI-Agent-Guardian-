def test_list_agents(client):
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) >= 5
    agent_names = [a["name"] for a in agents]
    assert "Agent Alpha" in agent_names
    assert "Agent Gamma" in agent_names

    # Check risk attributes are populated
    for agent in agents:
        assert "risk_score" in agent
        assert "risk_level" in agent
        assert agent["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_get_agent_detail(client):
    response = client.get("/api/agents/agent-gamma")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "agent-gamma"
    assert data["name"] == "Agent Gamma"
    assert "risk_explanation" in data
    assert data["risk_explanation"]["risk_level"] in ["HIGH", "CRITICAL"]
    assert len(data["events"]) > 0

def test_get_agent_not_found(client):
    response = client.get("/api/agents/non-existent-agent-999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "AGENT_NOT_FOUND"
