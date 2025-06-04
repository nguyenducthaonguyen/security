from datetime import datetime, timedelta, timezone

import asyncio
from fastapi import APIRouter, HTTPException, Depends, Response, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.cores import auth
from app.cores.dependencies import get_db, get_current_user
from app.models.users import User
from app.schemas.active_access_tokens import ActiveAccessTokenCreate
from app.schemas.response import StandardResponse
from app.schemas.session import SessionCreate
from app.schemas.token_log import TokenLogCreate
from app.schemas.users import UserCreate, UserRead, TokenResponse
from app.services.active_access_token_service import ActiveAccessTokenService
from app.services.auth_service import AuthService
from app.services.blacklist_token_service import BlacklistTokenService
from app.services.rate_limiter_service import RateLimiterService
from app.services.session_service import SessionService
from app.services.token_log_service import TokenLogService


router = APIRouter()


@router.post("/register", response_model=StandardResponse[UserRead])
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Kiểm tra username và email đã tồn tại chưa
    auth_service = AuthService(db)
    new_user = auth_service.register_user(user)
    return {
        "status_code": 200,
        "message": "Success",
        "data": new_user
    }


@router.post("/login", response_model=StandardResponse[TokenResponse])
def login(
    response: Response,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password):
        if user:
            safe_log_token_action(db, user, "login failed", request)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.status:
        raise HTTPException(status_code=401, detail="User blocked")

    # Tạo access token và refresh token
    access_token = auth.create_access_token(data={"sub": user.username})
    refresh_token = auth.create_refresh_token(data={"sub": user.username})

    # Lưu access token vào DB
    save_access_token(db, access_token, user.id)

    # Set refresh token trong cookie HttpOnly
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # chỉ dùng HTTPS
        samesite="strict",
        max_age=7 * 24 * 3600,  # 7 ngày
    )

    safe_log_token_action(db, user, "login", request)
    log_session(db, refresh_token, request, user)

    return {
        "status_code": 200,
        "message": "Success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "id": user.id,
            "username": user.username,
        }
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    username = decode_refresh_token_or_raise(refresh_token)

    user = db.query(User).filter(User.username == username).first()
    if not user or not user.status:
        raise HTTPException(status_code=401, detail="User not found or blocked")

    validate_refresh_session_or_raise(db, refresh_token)

    new_access_token = auth.create_access_token(data={"sub": user.username})
    save_access_token(db, new_access_token, user.id)

    safe_log_token_action(db, user, "refresh", request)

    # Trả token mới (client dùng để gọi API)
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "id": user.id,
        "username": user.username,
    }


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token missing")

    session_service = SessionService(db)
    token_service = ActiveAccessTokenService(db)
    success = session_service.revoke_session(refresh_token)

    # Blacklist access token lấy từ header Authorization
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        access_token = auth_header.split(" ")[1]
        blacklist_service = BlacklistTokenService(db)
        blacklist_service.blacklist_token(access_token)
        token_service.delete_token(access_token)
    response.delete_cookie("refresh_token")

    if not success:
        raise HTTPException(status_code=400, detail="Session not found")

    return {
        "status_code": 200,
        "message": "Logged out successfully"}


@router.post("/logout-all")
def logout_all(
    response: Response,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session_service = SessionService(db)
    session_service.revoke_all_sessions(user.id)

    token_service = ActiveAccessTokenService(db)
    blacklist_service = BlacklistTokenService(db)

    active_tokens = token_service.get_tokens_by_user_id(user.id)
    for token in active_tokens:
        blacklist_service.blacklist_token(token.access_token)

    token_service.delete_tokens_by_user_id(user.id)

    response.delete_cookie("refresh_token")
    return {
        "status_code": 200,
        "message": "Logged out from all sessions"}


# --- Helper functions ---
def safe_log_token_action(db: Session, user: User, action: str, request: Request):
    """Ghi log hành động token, tránh lỗi gây crash."""
    try:
        log_token_action(db, user, action, request)
    except Exception:
        pass


def log_token_action(db: Session, user: User, action: str, request: Request):
    log_service = TokenLogService(db)
    ip = request.client.host
    agent = request.headers.get("user-agent")

    log_data = TokenLogCreate(
        user_id=user.id,
        username=user.username,
        ip_address=ip,
        user_agent=agent,
        action=action,
    )
    log_service.log_token_request(log_data)

    if log_service.is_suspicious(user.id, ip, agent, action):
        suspicious_log = TokenLogCreate(**{**log_data.dict(), "action": f"suspicious {action} detected"})
        log_service.log_token_request(suspicious_log)


def log_session(db: Session, refresh_token: str, request: Request, user: User):
    session_service = SessionService(db)
    session_data = SessionCreate(
        user_id=user.id,
        refresh_token=refresh_token,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    try:
        session_service.create_session(session_data)
    except Exception:
        raise HTTPException(status_code=401, detail="Session creation failed")


def decode_refresh_token_or_raise(token: str) -> str:
    """Giải mã refresh token và trả về username hoặc raise lỗi."""
    try:
        payload = auth.decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return username
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


def validate_refresh_session_or_raise(db: Session, refresh_token: str):
    session_service = SessionService(db)
    if not session_service.validate_refresh_session(refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token revoked or expired")


def save_access_token(db: Session, access_token: str, user_id: int):
    token_service = ActiveAccessTokenService(db)
    token_create = ActiveAccessTokenCreate(
        user_id=user_id,
        access_token=access_token,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),  # ví dụ expire 30 phút
    )
    token_service.create_token(token_create)
