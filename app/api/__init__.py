from fastapi import APIRouter, Depends
from app.api import admins, posts, users, auth
from app.cores.dependencies import require_roles
from app.models.users import RoleEnum

api_router = APIRouter()

api_router.include_router(posts.router, prefix="/posts", tags=["posts"], dependencies=[Depends(require_roles(RoleEnum.admin, RoleEnum.user))])
api_router.include_router(users.router, prefix="/users", tags=["users"], dependencies=[Depends(require_roles(RoleEnum.admin, RoleEnum.user))])
api_router.include_router(admins.router, prefix="/admins", tags=["admins"], dependencies=[Depends(require_roles(RoleEnum.admin))])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
