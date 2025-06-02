from sqlalchemy.orm import Session
from app.models.blacklisted_tokens import BlacklistedToken
from app.schemas.blacklist_token import BlacklistedTokenCreate

class BlacklistedTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, token_data: BlacklistedTokenCreate) -> BlacklistedToken:
        db_token = BlacklistedToken(**token_data.model_dump())
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def is_blacklisted(self, token: str) -> bool:
        return self.db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None
