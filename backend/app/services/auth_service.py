from sqlalchemy.orm import Session
from ..database.models import User
from ..core.security import verify_password, hash_password, create_access_token
from ..core.errors import GuardianAPIException

def authenticate_user(db: Session, username_or_email: str, password: str):
    """Authenticate a user by username or email and return session token."""
    user = db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user:
        raise GuardianAPIException(
            code="INVALID_CREDENTIALS",
            message="Invalid username/email or password.",
            status_code=401
        )

    if not verify_password(password, user.password_hash, user.salt):
        raise GuardianAPIException(
            code="INVALID_CREDENTIALS",
            message="Invalid username/email or password.",
            status_code=401
        )

    token = create_access_token(user.id, user.username, user.role)
    return token, user

def register_user(db: Session, username: str, email: str, password: str, role: str = "admin") -> User:
    """Register a new user with salted hashed credentials."""
    existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing:
        raise GuardianAPIException(
            code="USER_ALREADY_EXISTS",
            message="A user with that username or email already exists.",
            status_code=409
        )

    pwd_hash, salt = hash_password(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=pwd_hash,
        salt=salt,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
