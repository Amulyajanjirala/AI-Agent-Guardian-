def test_list_events(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    events = response.json()
    assert len(events) > 10

def test_filter_events_by_severity(client):
    response = client.get("/api/events?severity=CRITICAL")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 2
    for evt in events:
        assert evt["severity"] == "CRITICAL"

def test_filter_events_by_agent(client):
    response = client.get("/api/events?agent_id=agent-gamma")
    assert response.status_code == 200
    events = response.json()
    assert len(events) >= 3
    for evt in events:
        assert evt["agent_id"] == "agent-gamma"

def test_get_event_by_id(client):
    response = client.get("/api/events/evt-001")
    assert response.status_code == 200
    evt = response.json()
    assert evt["id"] == "evt-001"
    assert evt["agent_id"] == "agent-gamma"
    assert evt["severity"] == "CRITICAL"

def test_event_not_found(client):
    response = client.get("/api/events/evt-unknown-999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "EVENT_NOT_FOUND"
