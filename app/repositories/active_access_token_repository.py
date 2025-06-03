from datetime import datetime, timezone
from os import access
from typing import List

from sqlalchemy.orm import Session

from app.models.active_access_tokens import ActiveAccessToken
from app.schemas.active_access_tokens import ActiveAccessTokenCreate


class ActiveAccessTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, token_data: ActiveAccessTokenCreate) -> ActiveAccessToken:
        db_token = ActiveAccessToken(**token_data.model_dump())
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_access_tokens_by_user_id(self, user_id: int) -> List[ActiveAccessToken]:
        access_tokens = self.db.query(ActiveAccessToken).filter_by(user_id=user_id).all()
        return access_tokens

    def delete_token(self, token: str) -> bool:
        try:
            deleted_count = (
                self.db.query(ActiveAccessToken)
                .filter_by(access_token=token)
                .delete(synchronize_session=False)
            )
            self.db.commit()
            return deleted_count > 0
        except Exception:
            self.db.rollback()
            return False

    def delete_tokens_by_user_id(self, user_id: int) -> bool:
        try:
            deleted_count = (
                self.db.query(ActiveAccessToken)
                .filter_by(user_id=user_id)
                .delete(synchronize_session=False)
            )
            self.db.commit()
            return deleted_count > 0
        except Exception:
            self.db.rollback()
            return False

    def delete_expired_tokens(self):
        expired_tokens = (
            self.db.query(ActiveAccessToken)
            .filter(ActiveAccessToken.expires_at < datetime.now(timezone.utc))
            .all()
        )
        for token in expired_tokens:
            self.db.delete(token)
        self.db.commit()


