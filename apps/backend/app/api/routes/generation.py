from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class StartGenerationRequest(BaseModel):
    approved: bool


@router.post("/episodes/{episode_id}/generation", status_code=202)
def start_generation(episode_id: str, payload: StartGenerationRequest):
    state = "running" if payload.approved else "blocked"
    return {
        "success": payload.approved,
        "data": {
            "episode_id": episode_id,
            "stage_name": "episode_generation",
            "state": state,
        },
    }
