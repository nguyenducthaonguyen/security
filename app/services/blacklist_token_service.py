from sqlalchemy.orm import Session
from app.schemas.blacklist_token import BlacklistedTokenCreate
from app.repositories.blacklist_token_repository import BlacklistedTokenRepository

class BlacklistTokenService:
    def __init__(self, db: Session):
        self.repo = BlacklistedTokenRepository(db)

    def blacklist_token(self, token: str):
        token_data = BlacklistedTokenCreate(token=token)
        return self.repo.add(token_data)

    def is_token_blacklisted(self, token: str) -> bool:
        return self.repo.is_blacklisted(token)
