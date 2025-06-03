from datetime import datetime, timedelta, timezone

from app.repositories.rate_limiter_repository import RateLimiterRepository


class RateLimiterService:
    def __init__(self, repo: RateLimiterRepository):
        self.repo = repo

    def is_rate_limited(self, token: str, max_requests: int = 10, period_seconds: int = 1) -> bool:
        now = datetime.now(timezone.utc)
        period_start = now - timedelta(seconds=period_seconds)

        count = self.repo.count_token_usage(token, period_start)
        self.repo.log_token_usage(token, now)

        return count >= max_requests

    def blacklist_token(self, token: str):
        self.repo.blacklist_token(token)

    def cleanup_expired_tokens(self, expire_minutes: int = 1):
        expire_time = datetime.now(timezone.utc) - timedelta(minutes=expire_minutes)
        self.repo.delete_expired_tokens(expire_time)