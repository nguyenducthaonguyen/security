from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from fastapi import Request, HTTPException

from app.cores.dependencies import get_db
from app.services.blacklist_token_service import BlacklistTokenService
from app.cores.auth_utils import validate_token_and_get_user


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

        try:
            blacklist_service = BlacklistTokenService(db)
            if blacklist_service.is_token_blacklisted(token):
                return JSONResponse(status_code=401, content={"detail": "Token has been revoked"})

            user = validate_token_and_get_user(token, db)
            request.state.user = user.username  # hoặc gán luôn object nếu cần

        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
        except Exception:
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

        return await call_next(request)
