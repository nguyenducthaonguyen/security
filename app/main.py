from fastapi import FastAPI
from app.api import api_router
from app.middleware.access_log import AccessLogMiddleware


app = FastAPI(title="FastAPI Security 5")

app.add_middleware(AccessLogMiddleware)

app.include_router(api_router, prefix="/api/v1")
