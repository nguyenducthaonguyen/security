from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import JWTError, ExpiredSignatureError
from fastapi.exceptions import HTTPException
from app.cores import auth
from app.cores.dependencies import get_db
from app.models.users import User
from app.services.blacklist_token_service import BlacklistTokenService


EXCLUDE_PATHS = ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/refresh"]

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXCLUDE_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})

        token = auth_header.split(" ")[1]

        db_generator = get_db()
        db = next(db_generator)

        blacklist_service = BlacklistTokenService(db)
        if blacklist_service.is_token_blacklisted(token):
            return JSONResponse(status_code=401, content={"detail": "Token has been revoked"})

        try:
            payload = auth.decode_token(token)
            request.state.user = payload.get("sub")
            user = db.query(User).filter(User.username == payload.get("sub")).first()
            if not user or not user.status:
                return JSONResponse(status_code=401, content={"detail": "User blocked or not found"})

        except ExpiredSignatureError:
            return JSONResponse(status_code=401, content={"detail": "Access token expired"})
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired access token"})
        except HTTPException as e:
            # Bắt lỗi HTTPException nếu decode_token có raise thêm lỗi này
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception:
            # Bắt lỗi bất thường tránh crash app, trả lỗi 401 chung chung hoặc 500 tùy mong muốn
            return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})

        return await call_next(request)
