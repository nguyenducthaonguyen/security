from pydantic import BaseModel
from datetime import datetime

class SessionCreate(BaseModel):
    user_id: int
    refresh_token: str
    ip_address: str
    user_agent: str
    expires_at: datetime

class SessionRead(BaseModel):
    id: int
    user_id: int
    refresh_token: str
    ip_address: str
    user_agent: str
    created_at: datetime
    expires_at: datetime
    revoked: bool

    class Config:
        from_attributes = True
