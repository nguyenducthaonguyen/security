from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.cores.dependencies import get_db
from app.schemas.users import UserReadAdmin
from app.schemas.posts import MessageResponse
from app.services.user_service import UserService


router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/", response_model=list[UserReadAdmin])
def list_users(
    status: Optional[bool] = Query(None, description="Trạng thái người dùng: true = active, false = blocked"),
    service: UserService = Depends(get_user_service)
):
    """
    Lấy danh sách người dùng theo trạng thái.
    """
    return service.list_users(status)


@router.get("/users/{user_id}", response_model=UserReadAdmin)
def get_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Lấy thông tin chi tiết người dùng theo ID.
    """
    return service.get_user_by_id_for_admin(user_id)


@router.patch("/users/{user_id}/block", response_model=MessageResponse)
def block_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Admin khóa tài khoản người dùng.
    """
    return service.block_user_for_admin(user_id)


@router.patch("/users/{user_id}/unblock", response_model=MessageResponse)
def unblock_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Admin mở khóa tài khoản người dùng.
    """
    return service.unblock_user_for_admin(user_id)


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    """
    Admin xóa người dùng cùng tất cả bài viết của họ.
    """
    return service.delete_user(user_id)
