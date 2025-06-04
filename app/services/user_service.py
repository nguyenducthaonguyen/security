from typing import Optional

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.cores import auth
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserUpdateRequest, PasswordChangeRequest, MessageResponse
from app.models.users import User

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> User:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.status:
            raise HTTPException(status_code=403, detail="User blocked")
        return user

    def get_user_by_email(self, email: str) -> User:
        user = self.repo.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_users_by_role_user(self) -> list[User]:
        return self.repo.get_users_by_role_user()

    def update_user(self, user_id: int, update_data: UserUpdateRequest) -> User:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if update_data.email != user.email:
            existing_user = self.repo.get_user_by_email(update_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(status_code=400, detail="Email already registered")

        user.email = update_data.email
        user.fullname = update_data.fullname
        user.gender = update_data.gender

        self.repo.update_user(user)
        return user

    def update_user_password(self, user_id: int, data: PasswordChangeRequest) -> MessageResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not auth.verify_password(data.password_old, user.password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")

        new_password_hash = auth.get_password_hash(data.password)
        self.repo.update_password(user, new_password_hash)

        return MessageResponse(detail="Password updated successfully")

    def block_user(self, user_id: int) -> MessageResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        self.repo.block_user(user)
        return MessageResponse(detail="User blocked successfully")

    def list_users(self, status: bool | None = None) -> list[User]:
        return self.repo.list_users(status)

    # Admin-specific services
    def get_user_by_id_for_admin(self, user_id: int) -> User:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def block_user_for_admin(self, user_id: int) -> MessageResponse:
        user = self.get_user_by_id_for_admin(user_id)
        if not user.status:
            return MessageResponse(detail="User was already blocked")
        self.repo.block_user(user)
        return MessageResponse(detail="User blocked successfully")

    def unblock_user_for_admin(self, user_id: int) -> MessageResponse:
        user = self.get_user_by_id_for_admin(user_id)
        if user.status:
            return MessageResponse(detail="User was already unblocked")
        self.repo.unblock_user(user)
        return MessageResponse(detail="User unblocked successfully")

    def delete_user(self, user_id: int) -> MessageResponse:
        try:
            user = self.repo.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            self.repo.delete_user_and_posts(user)

            return MessageResponse(detail="User and their posts deleted successfully")

        except SQLAlchemyError:
            raise HTTPException(status_code=500, detail="An error occurred while deleting the user")

    def get_users_with_posts_paginated(self, page: int, limit: int, name: Optional[str] = None, status: Optional[bool] = None):
        skip = (page - 1) * limit
        users = self.repo.get_users_with_posts(skip, limit, name, status)
        total = self.repo.count_users(name, status)

        last_page = (total - 1) // limit + 1

        return {
            "status_code": 200,
            "message": "Success",
            "data": users,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": skip
            },
            "link": {
                "self": f"http://127.0.0.1:8000/api/v1/admins/users-with-posts?page={page}&limit={limit}",
                "next": f"http://127.0.0.1:8000/api/v1/admins/users-with-posts?page={page + 1}&limit={limit}" if page < last_page else None,
                "last": f"http://127.0.0.1:8000/api/v1/admins/users-with-posts?page={last_page}&limit={limit}"
            }
        }