from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.cores.database import Base

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=False, nullable=False, index=True)
    blacklisted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
