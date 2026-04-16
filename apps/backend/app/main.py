from fastapi import FastAPI

from app.api.routes.analysis import router as analysis_router
from app.api.routes.assets import router as assets_router
from app.api.routes.generation import router as generation_router
from app.api.routes.health import router as health_router
from app.api.routes.review import router as review_router

app = FastAPI(title="anime-with-her director console")
app.include_router(health_router, prefix="/api/v1")
app.include_router(assets_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(generation_router, prefix="/api/v1")
app.include_router(review_router, prefix="/api/v1")
