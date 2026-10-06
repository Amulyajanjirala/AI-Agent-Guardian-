# AI Agent Guardian — Intelligent Security & Risk Monitoring Platform

> *"Monitor. Analyze. Protect. Approve."*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](#license)

**AI Agent Guardian** is a cybersecurity and risk monitoring platform designed specifically for autonomous AI agents. As autonomous agents are granted tool execution permissions, database access, and external API capabilities, traditional firewall and IAM perimeters fall short. AI Agent Guardian continuously monitors AI agent activities, analyzes telemetry logs, detects behavioral anomalies, calculates explainable risk scores, and provides an interactive conversational Guardian chatbot for security investigations.

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Objectives](#objectives)
3. [Core Features (Version 1)](#core-features-version-1)
4. [Architecture](#architecture)
5. [Technology Stack](#technology-stack)
6. [Project Structure](#project-structure)
7. [Installation & Setup](#installation--setup)
8. [Running the Application](#running-the-application)
9. [API Documentation](#api-documentation)
10. [Database Schema](#database-schema)
11. [Risk Engine Specification](#risk-engine-specification)
12. [Chatbot Intents](#chatbot-intents)
13. [Version Roadmap (V1 to V5)](#version-roadmap-v1-to-v5)
14. [Security Considerations](#security-considerations)
15. [Automated Testing](#automated-testing)
16. [Screenshots & UI Previews](#screenshots--ui-previews)

---

## Problem Statement

Autonomous AI agents (such as code generators, customer service bots, and DevOps automators) are increasingly entrusted with significant execution privileges. However:
- **Unrestricted Tool Execution**: AI agents may generate unauthorized tool calls (e.g., executing arbitrary shell commands, modifying file permissions).
- **Credential & Sensitive Resource Probing**: Compromised or malfunctioning prompts may cause agents to access confidential files (`/etc/secrets/vault.token`, internal databases).
- **Traffic Spikes & Token Burn**: Runaway loops or malicious injections can drive anomalous request frequencies and Denial of Service (DoS).
- **Lack of Explainable Oversight**: Security operations centers (SOC) lack visibility into agent behavior and need clear explanations for why an agent is flagged as high-risk.

---

## Objectives

- Provide a single pane of glass for monitoring AI agent fleet health, activity frequency, and threat indicators.
- Compute transparent, deterministic, and explainable risk scores based on event severity, event frequency, and suspicious patterns.
- Deliver an interactive, security-focused chatbot ("Guardian") that allows administrators to query fleet status and investigate specific agent risks via natural language.
- Establish a clean, decoupled service architecture ready to incorporate real LLM providers (NVIDIA NIM APIs), tool routers, policy engines, and behavioral anomaly detectors in subsequent phases.

---

## Core Features (Version 1)

- **Dark Cybersecurity UI**: Designed with high-contrast, professional cybersecurity aesthetics (navy/black background, neon cyan accents, severity pills, risk progress bars).
- **Security Dashboard**:
  - Top telemetry stats: Total Agents, Active Agents, Security Events, High Risk Count.
  - Live system status indicators: `Guardian Status: ONLINE`, `Security Status: MONITORING`.
  - Agent Fleet Risk Table with risk score bars, status badges, and an interactive **Inspect** modal for drilldowns.
  - Live Security Events stream with severity badges, timestamps, target agents, and data sources.
- **Explainable Risk Engine (`risk_engine.py`)**:
  - Deterministic severity points: `INFO: 5`, `LOW: 15`, `MEDIUM: 30`, `HIGH: 50`, `CRITICAL: 80`.
  - Combines base severity points with recency factors and pattern multipliers.
  - Classifies agents into 4 tiers:
    - `0–29`: **LOW**
    - `30–59`: **MEDIUM**
    - `60–79`: **HIGH**
    - `80–100`: **CRITICAL**
  - Generates clear, human-readable justification reasons and actionable operational recommendations.
- **Guardian Conversational Assistant (`chat_service.py`)**:
  - Intent-based chatbot handling natural inquiries without requiring an external LLM in V1.
  - Extracts targets and understands queries such as:
    - *"Show me high risk agents"*
    - *"Why is Agent Gamma high risk?"*
    - *"What security events happened recently?"*
    - *"Give me today's security summary"*
    - *"Which agent has the highest risk?"*
    - *"Is Agent Alpha behaving normally?"*
  - Injects rich structured telemetry cards into chat bubbles.
  - Persistent conversation sessions and history stored in SQLite.
- **Authentication & Security**:
  - PBKDF2 password hashing with SHA-256 and unique 16-byte random salts (NIST-compliant).
  - Bearer token session authentication.
  - Centralized error handlers preventing internal stack trace disclosure.

---

## Architecture

```
                                    USER
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
             Web Dashboard                      Guardian Chat
        (dashboard.html / js)                  (chat.html / js)
                    │                                 │
                    └────────────────┬────────────────┘
                                     │ REST / JSON
                                     ▼
                    ┌─────────────────────────────────┐
                    │      FastAPI Application        │
                    │   (CORS / Middleware / Errors)  │
                    └────────────────┬────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
  Auth Service                  Risk Engine                 Chat Service
  (PBKDF2 Hashing /             (Severity Points /          (Intent Engine /
   Token Sessions)               Score / Clamping)           LLMService Abstr.)
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     │
                                     ▼
                          SQLAlchemy ORM Layer
                                     │
                                     ▼
                        SQLite Database (guardian.db)
```

---

## Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Starlette
- **Database & ORM**: SQLite, SQLAlchemy 2.0+
- **Security & Crypto**: Python standard `hashlib` (PBKDF2-HMAC-SHA256, 100,000 iterations), `secrets`
- **Frontend**: Modern HTML5, CSS3 (Cyber Dark theme, CSS Grid & Flexbox), Vanilla JavaScript (ES6+ Fetch API, no heavy node build steps required)
- **Testing**: Pytest, FastAPI TestClient, HTTPX
- **Future AI Layer**: NVIDIA NIM / OpenAI-compatible API Service Layer abstraction (`llm_service.py`)

---

## Project Structure

```
ai-agent-guardian/
├── .env.example              # Environment variables template
├── .env                      # Local configuration file
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
│
├── data/
│   └── guardian.db           # SQLite database (auto-generated)
│
├── frontend/
│   ├── index.html            # Product landing page & entrypoint
│   ├── login.html            # Cybersecurity-themed login terminal
│   ├── dashboard.html        # Main security operations dashboard
│   ├── chat.html             # Guardian conversational investigation UI
│   ├── css/
│   │   ├── style.css         # Theme variables, badges, buttons, cards
│   │   ├── dashboard.css     # Sidebar, stats grid, tables, inspector modal
│   │   └── chat.css          # Message bubbles, prompt chips, cards
│   └── js/
│       ├── api.js            # Centralized API client & toast notifications
│       ├── auth.js           # Session auth, login handling & logout
│       ├── dashboard.js      # Dashboard telemetry rendering & inspector
│       └── chat.js           # Chat stream, intent handling, suggestion chips
│
└── backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py           # FastAPI entrypoint & static file mounts
    │   ├── core/
    │   │   ├── config.py     # Settings and environment loader
    │   │   ├── security.py   # PBKDF2 hashing & session tokens
    │   │   └── errors.py     # Standardized JSON error handlers
    │   ├── database/
    │   │   ├── database.py   # SQLAlchemy engine & session dependency
    │   │   ├── models.py     # User, Agent, SecurityEvent, Chat models
    │   │   └── seed.py       # Initial mock agents and telemetry seeder
    │   ├── schemas/
    │   │   ├── auth.py       # Pydantic schemas for authentication
    │   │   ├── agent.py      # Agent and risk explanation schemas
    │   │   ├── event.py      # Security event schemas
    │   │   ├── dashboard.py  # Dashboard telemetry schemas
    │   │   └── chat.py       # Chat query and response schemas
    │   ├── services/
    │   │   ├── auth_service.py   # User verification & registration
    │   │   ├── risk_engine.py    # Deterministic risk scoring algorithm
    │   │   ├── agent_service.py  # Agent queries & score recalculation
    │   │   ├── event_service.py  # Event filtering & ingestion
    │   │   ├── llm_service.py    # Abstract LLM layer (ready for NVIDIA V2)
    │   │   └── chat_service.py   # Intent detector & conversational builder
    │   └── api/
    │       ├── auth.py       # POST /api/auth/login, GET /api/auth/me
    │       ├── agents.py     # GET /api/agents, GET /api/agents/{id}
    │       ├── events.py     # GET /api/events, GET /api/events/{id}
    │       ├── dashboard.py  # GET /api/dashboard
    │       ├── risk.py       # GET /api/risk, GET /api/risk/{agent_id}
    │       └── chat.py       # POST /api/chat, GET /api/chat/history/{id}
    └── tests/
        ├── conftest.py       # Shared in-memory test database fixture
        ├── test_auth.py      # Auth and password verification tests
        ├── test_agents.py    # Agent querying and 404 tests
        ├── test_events.py    # Security event filtering tests
        ├── test_risk_engine.py # Risk engine formula & threshold tests
        ├── test_chat.py      # Intent-based chat queries & history tests
        └── test_dashboard_and_risk.py # Fleet metrics tests
```

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ai-agent-guardian.git
cd ai-agent-guardian
```

### 2. Create and Activate Virtual Environment (Optional but Recommended)
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

---

## Running the Application

### Start the Unified Backend & Frontend Server
The FastAPI backend serves both the REST API and the frontend static assets automatically:

```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

When started, database tables and realistic mock security data are seeded automatically on first launch!

### Access the Web Interfaces:
- **Landing Page**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Login Terminal**: [http://127.0.0.1:8000/login.html](http://127.0.0.1:8000/login.html)
- **Security Dashboard**: [http://127.0.0.1:8000/dashboard.html](http://127.0.0.1:8000/dashboard.html)
- **Guardian Chatbot**: [http://127.0.0.1:8000/chat.html](http://127.0.0.1:8000/chat.html)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Default Demonstration Credentials:
| Role | Username / Email | Password |
|---|---|---|
| Security Administrator | `admin` (or `admin@guardian.local`) | `admin123` |
| Security Analyst | `analyst` (or `analyst@guardian.local`) | `analyst123` |

---

## API Documentation

All endpoints return standardized JSON. In case of error, response adheres to:
```json
{
  "success": false,
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID 'agent-xyz' does not exist."
  }
}
```

### Core Endpoints:
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health status and operational status (`ONLINE`, `MONITORING`) |
| `POST` | `/api/auth/login` | Authenticate user and issue Bearer token |
| `GET` | `/api/auth/me` | Fetch authenticated user profile |
| `GET` | `/api/dashboard` | Fleet totals, risk distribution, recent alerts |
| `GET` | `/api/agents` | List all monitored agents with current risk scores |
| `GET` | `/api/agents/{agent_id}` | Detailed agent profile, event log, risk explanation |
| `GET` | `/api/events` | List security events (supports `?agent_id=&severity=&limit=`) |
| `GET` | `/api/events/{event_id}` | Fetch individual security event |
| `GET` | `/api/risk` | Fleet risk report and top risk drivers |
| `GET` | `/api/risk/{agent_id}` | Detailed risk breakdown and security recommendations |
| `POST` | `/api/chat` | Send message to Guardian Chatbot (intent parsing) |
| `GET` | `/api/chat/sessions` | List recent conversation sessions |
| `GET` | `/api/chat/history/{id}` | Retrieve messages in a conversation session |

---

## Risk Engine Specification

The Version 1 Risk Engine calculates a transparent, deterministic score between `0` and `100`:

1. **Severity Points**:
   - `INFO`: 5 pts
   - `LOW`: 15 pts
   - `MEDIUM`: 30 pts
   - `HIGH`: 50 pts
   - `CRITICAL`: 80 pts
2. **Formula**:
   $$\text{Base Score} = \min\left(60, \sum \text{Severity Points} \times 0.45\right)$$
   $$\text{Frequency Factor} = \min\left(20, \text{Events in last 24h} \times 3\right)$$
   $$\text{Pattern Penalty} = \min\left(20, \text{Critical Count} \times 12\right) + \min\left(10, \max(0, \text{High Count} - 1) \times 5\right)$$
   $$\text{Final Score} = \text{clamp}\left(\text{Base Score} + \text{Frequency Factor} + \text{Pattern Penalty}, 0, 100\right)$$
3. **Risk Levels**:
   - `0 - 29`: **LOW**
   - `30 - 59`: **MEDIUM**
   - `60 - 79`: **HIGH**
   - `80 - 100`: **CRITICAL**

---

## Chatbot Intents

In Version 1, the chatbot uses pattern matching and semantic token extraction:
- `GET_AGENTS`: "Show all agents", "List registered agents"
- `GET_HIGH_RISK_AGENTS`: "Show high risk agents", "Which agents are critical?"
- `GET_SECURITY_EVENTS`: "What security events happened recently?", "Show alerts"
- `GET_AGENT_RISK`: "Why is Agent Gamma high risk?", "Is Agent Alpha behaving normally?"
- `GET_SECURITY_SUMMARY`: "Give me today's security summary", "What's happening with my agents?"
- `GET_HIGHEST_RISK_AGENT`: "Which agent has the highest risk?", "Most risky agent"
- `UNKNOWN`: Graceful fallback providing helpful suggestion chips

---

## Version Roadmap (V1 to V5)

- [x] **Version 1 — Foundation (Current)**
  - Dark cybersecurity dashboard
  - Intent-based chatbot
  - SQLite database & SQLAlchemy ORM
  - Deterministic explainable risk engine
  - Mock AI agent telemetry & realistic security events
- [ ] **Version 2 — Real LLM + Tool Calling**
  - NVIDIA NIM LLM Integration via `llm_service.py`
  - Tool Router with schema validation (`get_agents`, `get_agent_risk`, `search_events`)
  - Grounded tool outputs without direct database access by LLM
- [ ] **Version 3 — Policy Engine + Permissions + Human Approval**
  - Granular RBAC and Action classification (LOW, MEDIUM, HIGH, CRITICAL)
  - Interactive approval workflow for sensitive operations (e.g., suspending agents)
  - Enforced principle: *AI recommends, Backend validates, Policy decides, Human approves*
- [ ] **Version 4 — Behavioral Anomaly Detection**
  - Agent behavior baselining (requests/hour, tool call distribution, access patterns)
  - Anomaly scoring and deviation confidence calculations
- [ ] **Version 5 — NVIDIA + Advanced AI/Security**
  - Correlated threat analysis across multiple agents
  - Natural language security investigation & automated mitigation playbooks

---

## Security Considerations

- **Password Storage**: Passwords are never stored in plaintext; salted and hashed using PBKDF2 with SHA-256 and 100,000 iterations.
- **SQL Injection Prevention**: All queries utilize SQLAlchemy ORM parameterized queries.
- **Environment Isolation**: API keys and secrets are loaded via environment variables (`.env`).
- **Safe Error Responses**: Internal stack traces are suppressed; uniform error codes returned to clients.

---

## Automated Testing

The project includes unit and integration tests across the risk engine, authentication, agent management, security events, dashboard telemetry, and chat intents.

Run tests using pytest:
```bash
pytest backend/tests -v
```

Output:
```
backend/tests/test_agents.py::test_list_agents PASSED
backend/tests/test_agents.py::test_get_agent_detail PASSED
backend/tests/test_agents.py::test_get_agent_not_found PASSED
backend/tests/test_auth.py::test_password_hashing PASSED
backend/tests/test_auth.py::test_login_success PASSED
backend/tests/test_auth.py::test_login_failure PASSED
backend/tests/test_auth.py::test_current_user_me PASSED
backend/tests/test_auth.py::test_unauthorized_access PASSED
backend/tests/test_chat.py::test_chat_high_risk_agents PASSED
backend/tests/test_chat.py::test_chat_agent_risk_explanation PASSED
backend/tests/test_chat.py::test_chat_security_summary PASSED
backend/tests/test_chat.py::test_chat_highest_risk_agent PASSED
backend/tests/test_chat.py::test_chat_unknown_intent PASSED
backend/tests/test_chat.py::test_chat_session_persistence PASSED
backend/tests/test_dashboard_and_risk.py::test_get_dashboard_summary PASSED
backend/tests/test_dashboard_and_risk.py::test_get_fleet_risk PASSED
backend/tests/test_dashboard_and_risk.py::test_get_individual_agent_risk PASSED
backend/tests/test_events.py::test_list_events PASSED
backend/tests/test_events.py::test_filter_events_by_severity PASSED
backend/tests/test_events.py::test_filter_events_by_agent PASSED
backend/tests/test_events.py::test_get_event_by_id PASSED
backend/tests/test_events.py::test_event_not_found PASSED
backend/tests/test_risk_engine.py::test_severity_points_mapping PASSED
backend/tests/test_risk_engine.py::test_risk_level_thresholds PASSED
backend/tests/test_risk_engine.py::test_empty_events_risk PASSED
backend/tests/test_risk_engine.py::test_critical_events_escalation PASSED
backend/tests/test_risk_engine.py::test_low_severity_events PASSED
backend/tests/test_risk_engine.py::test_generate_recommendation PASSED

======================== 28 passed in 0.65s ========================
```

---

## Screenshots & UI Previews

*(Screenshots placeholder for demonstration preview)*

1. **Security Operations Dashboard**: Displays real-time agent fleet stats, risk levels, and live telemetry feeds.
2. **Agent Risk Inspector**: Detailed modal with contributing factors, severity breakdown, and Guardian recommendations.
3. **Guardian Conversational Assistant**: Intent-driven security queries with interactive cards and prompt suggestions.
