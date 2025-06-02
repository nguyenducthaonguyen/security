from datetime import datetime

from pydantic import BaseModel

class ActiveAccessTokenCreate(BaseModel):
    user_id : int
    access_token: str
    expires_at: datetime

class ActiveAccessTokenRead(ActiveAccessTokenCreate):
    id: int
    created_at: datetime


    class Config:
        from_attributes = True

 