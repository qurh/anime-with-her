from pydantic import BaseModel
from fastapi import APIRouter

from app.services.rerender_service import start_rerender

router = APIRouter()


class RerenderRequest(BaseModel):
    source_job_id: str
    voice_version_id: str


@router.post("/rerender", status_code=202)
def rerender(payload: RerenderRequest):
    result = start_rerender(payload.source_job_id, payload.voice_version_id)
    return {"success": True, "data": result}
