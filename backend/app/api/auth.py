from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import Optional

from ..database.database import get_db
from ..schemas.auth import LoginRequest, LoginResponse, UserOut
from ..services.auth_service import authenticate_user
from ..core.security import verify_access_token
from ..core.errors import GuardianAPIException

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate security administrator and issue access token."""
    token, user = authenticate_user(db, payload.username_or_email, payload.password)
    return {
        "success": True,
        "token": token,
        "user": user
    }

@router.get("/me", response_model=UserOut)
def get_current_user(authorization: Optional[str] = Header(None)):
    """Retrieve details for current active session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise GuardianAPIException(
            code="UNAUTHORIZED",
            message="Valid authorization bearer token required.",
            status_code=401
        )
    token = authorization.split(" ")[1]
    session_data = verify_access_token(token)
    if not session_data:
        raise GuardianAPIException(
            code="SESSION_EXPIRED",
            message="Session has expired or token is invalid.",
            status_code=401
        )
    return {
        "id": session_data["user_id"],
        "username": session_data["username"],
        "email": f"{session_data['username']}@guardian.local",
        "role": session_data["role"]
    }
