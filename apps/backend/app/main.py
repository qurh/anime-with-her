from fastapi import FastAPI

from app.api.routes.assets import router as assets_router
from app.api.routes.health import router as health_router

app = FastAPI(title="anime-with-her director console")
app.include_router(health_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
