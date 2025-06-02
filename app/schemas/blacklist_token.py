from pydantic import BaseModel
from datetime import datetime

class BlacklistedTokenCreate(BaseModel):
    token: str

class BlacklistedTokenRead(BaseModel):
    id: int
    token: str
    blacklisted_at: datetime

    class Config:
        from_attributes = True
