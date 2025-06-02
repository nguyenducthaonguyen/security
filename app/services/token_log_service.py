from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from app.schemas.token_log import TokenLogCreate, TokenLogResponse
from app.repositories.token_log_repository import TokenLogRepository

class TokenLogService:
    def __init__(self, db: Session):
        self.repo = TokenLogRepository(db)

    def log_token_request(self, log_create: TokenLogCreate):
        return self.repo.create(log_create)

    def get_paginated (self, skip: int = 0, limit: int = 200) -> List[TokenLogResponse]:
        return self.repo.get_paginated(skip, limit)

    def is_suspicious(self, user_id: int, current_ip: str, current_agent: str, action: str) -> bool:
        last_log = self.repo.get_last_log(user_id, action)
        if not last_log:
            return False

        ip_changed = last_log.ip_address != current_ip
        agent_changed = last_log.user_agent != current_agent
        time_diff = datetime.utcnow() - last_log.timestamp

        if action == "login":
            return self._is_login_suspicious(ip_changed, agent_changed, time_diff)
        elif action == "refresh":
            return self._is_refresh_suspicious(time_diff)
        return False

    def _is_login_suspicious(self, ip_changed: bool, agent_changed: bool, time_diff: timedelta) -> bool:
        suspicious_time_window = timedelta(minutes=2)
        if (ip_changed or agent_changed) and time_diff < suspicious_time_window:
            return True
        return False

    def _is_refresh_suspicious(self, time_diff: timedelta) -> bool:
        suspicious_time_window = timedelta(seconds=10)
        return time_diff < suspicious_time_window
