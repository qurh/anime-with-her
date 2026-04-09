from fastapi import FastAPI

from .api.routes.health import router as health_router
from .api.routes.jobs import router as jobs_router

app = FastAPI()
app.include_router(health_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")