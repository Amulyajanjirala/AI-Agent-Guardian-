from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

class SecurityEventBase(BaseModel):
    agent_id: str
    event_type: str
    description: str
    severity: str
    source: str = "tool_monitor"

class SecurityEventCreate(SecurityEventBase):
    id: Optional[str] = None

class SecurityEventOut(SecurityEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: datetime
    agent_name: Optional[str] = None
