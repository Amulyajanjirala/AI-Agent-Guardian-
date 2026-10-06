def test_chat_high_risk_agents(client):
    res = client.post("/api/chat", json={"message": "Show me high risk agents"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "GET_HIGH_RISK_AGENTS"
    assert "detected" in data["response"].lower()
    assert len(data["data"]) > 0
    assert "session_id" in data

def test_chat_agent_risk_explanation(client):
    res = client.post("/api/chat", json={"message": "Why is Agent Gamma high risk?"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "GET_AGENT_RISK"
    assert "Agent Gamma" in data["response"]
    assert len(data["data"]) == 1
    assert "reasons" in data["data"][0]

def test_chat_security_summary(client):
    res = client.post("/api/chat", json={"message": "Give me today's security summary"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "GET_SECURITY_SUMMARY"
    assert "monitoring" in data["response"].lower()
    assert "ONLINE" in data["response"]

def test_chat_highest_risk_agent(client):
    res = client.post("/api/chat", json={"message": "Which agent has the highest risk?"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "GET_HIGHEST_RISK_AGENT"
    assert "highest risk score" in data["response"]

def test_chat_unknown_intent(client):
    res = client.post("/api/chat", json={"message": "Tell me a funny joke about space"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "UNKNOWN"
    assert "Guardian AI Security Assistant" in data["response"]

def test_chat_session_persistence(client):
    # Send first message
    res1 = client.post("/api/chat", json={"message": "Show me high risk agents"})
    sess_id = res1.json()["session_id"]

    # Send second message in same session
    res2 = client.post("/api/chat", json={"message": "Why is Agent Gamma high risk?", "session_id": sess_id})
    assert res2.json()["session_id"] == sess_id

    # Fetch session history
    hist_res = client.get(f"/api/chat/history/{sess_id}")
    assert hist_res.status_code == 200
    messages = hist_res.json()
    assert len(messages) >= 4  # 2 user messages + 2 guardian responses
