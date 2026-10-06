from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .core.config import settings
from .core.errors import (
    GuardianAPIException,
    guardian_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from .database.seed import seed_database
from .api import (
    auth_router,
    agents_router,
    events_router,
    dashboard_router,
    risk_router,
    chat_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed baseline security data on application startup."""
    seed_database()
    yield

app = FastAPI(
    title="AI Agent Guardian — Intelligent Security & Risk Monitoring Platform",
    description="Cybersecurity platform monitoring and protecting autonomous AI agents through behavioral analysis and transparent risk scoring.",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Error Handlers
app.add_exception_handler(GuardianAPIException, guardian_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API Routers
app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(events_router)
app.include_router(dashboard_router)
app.include_router(risk_router)
app.include_router(chat_router)

# Healthcheck Endpoint
@app.get("/api/health", tags=["System"])
def healthcheck():
    """System health check and operational status."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "guardian_status": "ONLINE",
        "security_status": "MONITORING",
        "timestamp": datetime.utcnow().isoformat()
    }

# Mount Frontend Static Assets
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", include_in_schema=False)
    @app.get("/index.html", include_in_schema=False)
    def serve_index():
        return FileResponse(frontend_dir / "index.html")

    @app.get("/login", include_in_schema=False)
    @app.get("/login.html", include_in_schema=False)
    def serve_login():
        return FileResponse(frontend_dir / "login.html")

    @app.get("/dashboard", include_in_schema=False)
    @app.get("/dashboard.html", include_in_schema=False)
    def serve_dashboard():
        return FileResponse(frontend_dir / "dashboard.html")

    @app.get("/chat", include_in_schema=False)
    @app.get("/chat.html", include_in_schema=False)
    def serve_chat():
        return FileResponse(frontend_dir / "chat.html")
