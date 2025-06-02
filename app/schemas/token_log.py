from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TokenLogCreate(BaseModel):
    user_id: Optional[int]
    username: Optional[str]
    ip_address: str
    user_agent: Optional[str]
    action: str

class TokenLogResponse(TokenLogCreate):
    id: int
    timestamp: datetime

    model_config = {
        "from_attributes": True  # Thay cho orm_mode = True trong Pydantic v1
    }