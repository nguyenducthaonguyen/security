import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import api_router
from app.cores.database import Base, engine
from app.cores.dependencies import get_db
from app.middleware.access_log import AccessLogMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.repositories.rate_limiter_repository import RateLimiterRepository
from app.services.active_access_token_service import ActiveAccessTokenService
from app.services.blacklist_token_service import BlacklistTokenService
from app.services.rate_limiter_service import RateLimiterService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async def cleanup_job():
        while True:
            db_gen = get_db()
            db = next(db_gen)
            try:
                blacklist_service = BlacklistTokenService(db)
                token_service = ActiveAccessTokenService(db)
                repo = RateLimiterRepository(db)
                token_usage_log = RateLimiterService(repo)
                blacklist_service.cleanup_expired_tokens(expire_minutes=30)
                token_service.cleanup_expired_tokens()
                token_usage_log.cleanup_expired_tokens(expire_minutes=1)
            finally:
                try:
                    next(db_gen)
                except StopIteration:
                    pass  # Generator đã hoàn tất

            await asyncio.sleep(600)

    asyncio.create_task(cleanup_job())
    yield  # Đây là phần bắt buộc để FastAPI chạy đúng lifecycle


# Khởi tạo app
app = FastAPI(title="FastAPI Security 5", lifespan=lifespan)

# Thêm middleware
app.add_middleware(AccessLogMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimiterMiddleware)

# Đăng ký router
app.include_router(api_router, prefix="/api/v1")

# Tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)


