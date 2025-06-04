from typing import Optional, List
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.models.users import User, RoleEnum
from app.models.posts import Post
from app.schemas.users import UserCreate, UserRead


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def _commit_and_refresh(self, obj: User):
        try:
            self.db.commit()
            self.db.refresh(obj)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user: User) -> UserRead:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_users_by_role_user(self) -> List[User]:
        return self.db.query(User).filter(User.role == RoleEnum.user).all()

    def update_user(self, user: User):
        self._commit_and_refresh(user)

    def update_password(self, user: User, new_password_hash: str):
        user.password = new_password_hash
        self._commit_and_refresh(user)

    def block_user(self, user: User):
        user.status = False
        self._commit_and_refresh(user)

    def unblock_user(self, user: User):
        user.status = True
        self._commit_and_refresh(user)

    def list_users(self, status: Optional[bool] = None, skip: int = 0, limit: int = 100) -> List[User]:
        query = self.db.query(User)
        if status is not None:
            query = query.filter(User.status == status)
        return query.offset(skip).limit(limit).all()

    def delete_user_and_posts(self, user: User):
        try:
            self.db.query(Post).filter(Post.user_id == user.id).delete(synchronize_session=False)
            self.db.delete(user)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def _filter_by_name_and_status(self, query, name: Optional[str], status: Optional[bool]):
        if name:
            query = query.filter(User.fullname.ilike(f"%{name}%"))
        if status is not None:
            query = query.filter(User.status == status)
        return query

    def get_users_with_posts(
            self,
            skip: int = 0,
            limit: int = 100,
            name: Optional[str] = None,
            status: Optional[bool] = None,
    ) -> List[User]:
        query = self.db.query(User).options(joinedload(User.posts))
        query = self._filter_by_name_and_status(query, name, status)
        return query.offset(skip).limit(limit).all()

    def count_users(self, name: Optional[str] = None, status: Optional[bool] = None) -> int:
        query = self.db.query(func.count(User.id))
        query = self._filter_by_name_and_status(query, name, status)
        return query.scalar()
