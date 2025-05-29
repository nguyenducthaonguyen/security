from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.users import User, RoleEnum
from app.models.posts import Post

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_users_by_role_user(self) -> List[User]:
        return self.db.query(User).filter(User.role == RoleEnum.user).all()

    def update_user(self, user: User):
        self.db.commit()
        self.db.refresh(user)

    def update_password(self, user: User, new_password_hash: str):
        user.password = new_password_hash
        self.db.commit()
        self.db.refresh(user)

    def block_user(self, user: User):
        user.status = False
        self.db.commit()
        self.db.refresh(user)

    def unblock_user(self, user: User):
        user.status = True
        self.db.commit()
        self.db.refresh(user)

    def list_users(self, status: bool | None = None) -> List[User]:
        query = self.db.query(User)
        if status is not None:
            query = query.filter(User.status == status)
        return query.all()

    def delete_user_and_posts(self, user: User):
        self.db.query(Post).filter(Post.user_id == user.id).delete()
        self.db.delete(user)
        self.db.commit()
