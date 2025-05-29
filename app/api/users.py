from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.models.users import User
from app.schemas.users import (UserRead, UserUpdateRequest, PasswordChangeRequest, MessageResponse)
from app.cores.dependencies import get_db, get_current_user


router = APIRouter()


# ✅ Local dependency cho service, chỉ dùng trong file này
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/", response_model=list[UserRead])
def list_active_users(
    service: UserService = Depends(get_user_service)
):
    return service.list_users(status=True)


@router.get("/me", response_model=UserRead)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.get_user_by_id(current_user.id)


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return service.get_user_by_id(user_id)


@router.put("/me", response_model=UserRead)
def update_current_user_info(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.update_user(current_user.id, user_update)


@router.patch("/me/change-password", response_model=MessageResponse)
def change_current_user_password(
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.update_user_password(current_user.id, password_data)


@router.delete("/me", response_model=MessageResponse)
def deactivate_current_user(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    return service.block_user(current_user.id)
