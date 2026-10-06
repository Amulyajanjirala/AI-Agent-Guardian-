import hashlib
import hmac
import os
import secrets
import time
from typing import Optional, Tuple, Dict

# In-memory token store for session tracking in V1
ACTIVE_SESSIONS: Dict[str, dict] = {}

def generate_salt(length: int = 16) -> str:
    """Generate a cryptographically secure random salt."""
    return secrets.token_hex(length)

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Hash a plaintext password using PBKDF2 with SHA-256 and 100,000 iterations.
    Returns (password_hash, salt).
    """
    if not salt:
        salt = generate_salt()
    
    dk = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return dk.hex(), salt

def verify_password(plain_password: str, password_hash: str, salt: str) -> bool:
    """Verify a plain password against the stored hash and salt."""
    computed_hash, _ = hash_password(plain_password, salt)
    return hmac.compare_digest(computed_hash, password_hash)

def create_access_token(user_id: int, username: str, role: str) -> str:
    """Generate a secure session token and track session."""
    token = f"agy_{secrets.token_urlsafe(32)}"
    ACTIVE_SESSIONS[token] = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "created_at": time.time(),
        "expires_at": time.time() + (24 * 3600)  # 24 hours
    }
    return token

def verify_access_token(token: str) -> Optional[dict]:
    """Verify session token and ensure it has not expired."""
    session = ACTIVE_SESSIONS.get(token)
    if not session:
        return None
    if time.time() > session["expires_at"]:
        del ACTIVE_SESSIONS[token]
        return None
    return session
