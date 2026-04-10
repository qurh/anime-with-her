from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes.budget import router as budget_router
from .api.routes.health import router as health_router
from .api.routes.jobs import router as jobs_router
from .api.routes.rerender import router as rerender_router
from .api.routes.uploads import router as uploads_router
from .api.routes.voice_registry import router as voice_registry_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(budget_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(jobs_router, prefix="/api/v1")
app.include_router(rerender_router, prefix="/api/v1")
app.include_router(uploads_router, prefix="/api/v1")
app.include_router(voice_registry_router, prefix="/api/v1")
