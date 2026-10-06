from pydantic import BaseModel, ConfigDict
from typing import Optional

class LoginRequest(BaseModel):
    username_or_email: str
    password: str
    remember_me: Optional[bool] = False

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: UserOut
