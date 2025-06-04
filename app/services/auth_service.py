from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.users import UserCreate, UserRead
from app.models.users import User
from app.cores import auth

class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register_user(self, user_data: UserCreate) -> UserRead:
        # Kiểm tra username đã tồn tại
        if self.repo.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        # Kiểm tra email đã tồn tại
        if self.repo.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )

        # Băm mật khẩu và tạo user mới
        hashed_password = auth.get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            password=hashed_password,
            email=user_data.email,
            fullname=user_data.fullname,
            gender=user_data.gender
        )

        return self.repo.create_user(new_user)
