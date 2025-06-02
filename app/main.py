from fastapi import FastAPI
from app.api import api_router
from app.cores.database import Base, engine
from app.middleware.access_log import AccessLogMiddleware
from app.middleware.auth_middleware import AuthMiddleware

app = FastAPI(title="FastAPI Security 5")

app.add_middleware(AccessLogMiddleware)
app.add_middleware(AuthMiddleware)

app.include_router(api_router, prefix="/api/v1")
Base.metadata.create_all(bind=engine)

