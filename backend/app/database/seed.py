"""
AI Agent Guardian - Database Seeding Module
Generates mock agents, realistic cybersecurity events, and administrator credentials.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import User, Agent, SecurityEvent
from ..core.security import hash_password
from ..services.risk_engine import calculate_risk_score

def seed_database(db: Session = None):
    """Seed initial users, agents, and security events if database is empty."""
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    target_engine = db.get_bind() if db is not None else engine
    Base.metadata.create_all(bind=target_engine)

    try:
        # Check if already seeded
        if db.query(User).first() is not None:
            return

        print("Seeding database with realistic AI cybersecurity data...")

        # 1. Seed Users
        admin_hash, admin_salt = hash_password("admin123")
        admin_user = User(
            username="admin",
            email="admin@guardian.local",
            password_hash=admin_hash,
            salt=admin_salt,
            role="admin",
            created_at=datetime.utcnow() - timedelta(days=30)
        )

        analyst_hash, analyst_salt = hash_password("analyst123")
        analyst_user = User(
            username="analyst",
            email="analyst@guardian.local",
            password_hash=analyst_hash,
            salt=analyst_salt,
            role="security_analyst",
            created_at=datetime.utcnow() - timedelta(days=15)
        )
        db.add_all([admin_user, analyst_user])
        db.flush()

        # 2. Seed Agents
        now = datetime.utcnow()
        agents_data = [
            Agent(
                id="agent-alpha",
                name="Agent Alpha",
                description="Autonomous customer support agent with access to ticketing and public knowledge base.",
                status="active",
                agent_type="customer_support",
                created_at=now - timedelta(days=20),
                last_activity=now - timedelta(minutes=4)
            ),
            Agent(
                id="agent-beta",
                name="Agent Beta",
                description="Financial analysis agent querying internal sales metrics and reporting warehouses.",
                status="active",
                agent_type="financial_analyst",
                created_at=now - timedelta(days=14),
                last_activity=now - timedelta(minutes=12)
            ),
            Agent(
                id="agent-gamma",
                name="Agent Gamma",
                description="DevOps automation agent with Kubernetes deployment and cluster orchestration privileges.",
                status="suspended",
                agent_type="devops_automator",
                created_at=now - timedelta(days=10),
                last_activity=now - timedelta(minutes=45)
            ),
            Agent(
                id="agent-delta",
                name="Agent Delta",
                description="Code generation and review assistant scanning pull requests and executing sandbox unit tests.",
                status="active",
                agent_type="code_generator",
                created_at=now - timedelta(days=7),
                last_activity=now - timedelta(minutes=2)
            ),
            Agent(
                id="agent-epsilon",
                name="Agent Epsilon",
                description="Data ingestion pipeline agent synchronizing telemetry logs to long-term storage.",
                status="active",
                agent_type="data_pipeline",
                created_at=now - timedelta(days=5),
                last_activity=now - timedelta(minutes=25)
            )
        ]
        db.add_all(agents_data)
        db.flush()

        # 3. Seed Realistic Security Events
        events_data = [
            # Agent Gamma events (High/Critical - suspended agent)
            SecurityEvent(
                id="evt-001",
                agent_id="agent-gamma",
                event_type="sensitive_resource_access",
                description="Unauthorized attempt to read '/etc/kubernetes/pki/ca.key' from host filesystem.",
                severity="CRITICAL",
                source="sandbox_telemetry",
                timestamp=now - timedelta(minutes=48)
            ),
            SecurityEvent(
                id="evt-002",
                agent_id="agent-gamma",
                event_type="suspicious_tool_call",
                description="Tool call 'exec_shell_command' invoked with unwhitelisted argument 'chmod 777 /var/run/docker.sock'.",
                severity="CRITICAL",
                source="tool_monitor",
                timestamp=now - timedelta(hours=1, minutes=15)
            ),
            SecurityEvent(
                id="evt-003",
                agent_id="agent-gamma",
                event_type="unusual_api_frequency",
                description="Burst traffic anomaly: 145 privileged API requests dispatched in 60 seconds to cluster gateway.",
                severity="HIGH",
                source="api_gateway",
                timestamp=now - timedelta(hours=2)
            ),
            SecurityEvent(
                id="evt-004",
                agent_id="agent-gamma",
                event_type="repeated_authentication_failure",
                description="5 failed mTLS handshakes detected within 120 seconds on vault ingress.",
                severity="HIGH",
                source="auth_proxy",
                timestamp=now - timedelta(hours=3, minutes=10)
            ),

            # Agent Beta events (Medium Risk)
            SecurityEvent(
                id="evt-005",
                agent_id="agent-beta",
                event_type="unusual_api_request",
                description="Queried non-standard internal sales endpoint '/api/v2/exec-payroll-summary'.",
                severity="MEDIUM",
                source="api_gateway",
                timestamp=now - timedelta(hours=1, minutes=40)
            ),
            SecurityEvent(
                id="evt-006",
                agent_id="agent-beta",
                event_type="high_request_frequency",
                description="Token burn rate increased 240% compared to typical baseline.",
                severity="MEDIUM",
                source="token_counter",
                timestamp=now - timedelta(hours=4)
            ),
            SecurityEvent(
                id="evt-007",
                agent_id="agent-beta",
                event_type="database_schema_inspection",
                description="Agent invoked metadata inspection query on restricted audit tables.",
                severity="LOW",
                source="db_guard",
                timestamp=now - timedelta(hours=6)
            ),

            # Agent Delta events (Medium Risk)
            SecurityEvent(
                id="evt-008",
                agent_id="agent-delta",
                event_type="unknown_endpoint_access",
                description="Outbound network socket request initiated to external IP 198.51.100.42:8443.",
                severity="HIGH",
                source="egress_firewall",
                timestamp=now - timedelta(hours=2, minutes=20)
            ),
            SecurityEvent(
                id="evt-009",
                agent_id="agent-delta",
                event_type="suspicious_tool_call",
                description="Tool 'git_clone' attempted download from untrusted external repository URI.",
                severity="MEDIUM",
                source="tool_monitor",
                timestamp=now - timedelta(hours=5)
            ),
            SecurityEvent(
                id="evt-010",
                agent_id="agent-delta",
                event_type="routine_code_scan",
                description="Standard pull request static code scan completed successfully.",
                severity="INFO",
                source="code_analyzer",
                timestamp=now - timedelta(hours=8)
            ),

            # Agent Alpha events (Low Risk - normal)
            SecurityEvent(
                id="evt-011",
                agent_id="agent-alpha",
                event_type="minor_validation_error",
                description="Customer query input contained invalid UTF-8 control sequences; sanitized.",
                severity="LOW",
                source="input_sanitizer",
                timestamp=now - timedelta(hours=3)
            ),
            SecurityEvent(
                id="evt-012",
                agent_id="agent-alpha",
                event_type="tool_execution",
                description="Customer support ticket #4928 successfully queried and updated.",
                severity="INFO",
                source="tool_monitor",
                timestamp=now - timedelta(hours=1)
            ),
            SecurityEvent(
                id="evt-013",
                agent_id="agent-alpha",
                event_type="heartbeat_ok",
                description="Agent telemetry heartbeat received within normal response time window (42ms).",
                severity="INFO",
                source="agent_health",
                timestamp=now - timedelta(minutes=4)
            ),

            # Agent Epsilon events (Low Risk)
            SecurityEvent(
                id="evt-014",
                agent_id="agent-epsilon",
                event_type="transient_network_timeout",
                description="Temporary 503 response from data lake sink; retried successfully after 3 seconds.",
                severity="LOW",
                source="pipeline_monitor",
                timestamp=now - timedelta(hours=7)
            ),
            SecurityEvent(
                id="evt-015",
                agent_id="agent-epsilon",
                event_type="batch_sync_complete",
                description="Synchronized 14,200 audit log records to immutable cold storage.",
                severity="INFO",
                source="pipeline_monitor",
                timestamp=now - timedelta(hours=2)
            ),
            SecurityEvent(
                id="evt-016",
                agent_id="agent-epsilon",
                event_type="heartbeat_ok",
                description="Agent heartbeat verified. Operational memory usage at 18%.",
                severity="INFO",
                source="agent_health",
                timestamp=now - timedelta(minutes=25)
            )
        ]
        db.add_all(events_data)
        db.flush()

        # 4. Calculate Initial Risk Scores for each agent
        for agent in agents_data:
            ag_events = [e for e in events_data if e.agent_id == agent.id]
            score, level, _, _ = calculate_risk_score(ag_events)
            agent.risk_score = score
            agent.risk_level = level

        db.commit()
        print("Database successfully initialized and seeded with 5 agents and 16 security events.")

    finally:
        if should_close:
            db.close()

if __name__ == "__main__":
    seed_database()
