from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.posts import PostCreate, PostUpdate, PostRead, MessageResponse

from app.models.users import User
from app.cores.dependencies import get_current_user, get_db
from app.services.post_service import PostService


router = APIRouter()


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)


@router.get("/", response_model=list[PostRead])
def get_all_posts(service: PostService = Depends(get_post_service)):
    return service.get_all_posts_active_users()


@router.get("/me", response_model=list[PostRead])
def get_my_posts(current_user: User = Depends(get_current_user), service: PostService = Depends(get_post_service)):
    return service.get_posts_by_user_id(current_user.id)


@router.get("/users/{user_id}", response_model=list[PostRead])
def get_posts_by_user(user_id: int, service: PostService = Depends(get_post_service)):
    return service.get_posts_by_user_id(user_id)


@router.post("/", response_model=PostRead)
def create_post(post: PostCreate, current_user: User = Depends(get_current_user), service: PostService = Depends(get_post_service)):
    return service.create_post(post, current_user.id)


@router.put("/{post_id}", response_model=MessageResponse)
def update_post(post_id: int, post: PostUpdate, current_user: User = Depends(get_current_user), service: PostService = Depends(get_post_service)):
    return service.update_post(post_id, post, current_user.id)


@router.get("/{post_id}", response_model=PostRead)
def get_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.get_post_by_id(post_id)


@router.delete("/{post_id}", response_model=MessageResponse)
def delete_post(post_id: int, current_user: User = Depends(get_current_user), service: PostService = Depends(get_post_service)):
    return service.delete_post(post_id, current_user.id)
