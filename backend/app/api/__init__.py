from .auth import router as auth_router
from .agents import router as agents_router
from .events import router as events_router
from .dashboard import router as dashboard_router
from .risk import router as risk_router
from .chat import router as chat_router

__all__ = [
    "auth_router",
    "agents_router",
    "events_router",
    "dashboard_router",
    "risk_router",
    "chat_router",
]
