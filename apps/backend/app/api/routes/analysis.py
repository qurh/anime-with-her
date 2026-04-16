from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class StartCharacterAnalysisRequest(BaseModel):
    source_video: str


class ApprovedCharacter(BaseModel):
    candidate_id: str
    display_name: str
    base_tone: str


class ApproveCharacterAnalysisRequest(BaseModel):
    approved_characters: list[ApprovedCharacter]


@router.post("/episodes/{episode_id}/analysis/character", status_code=202)
def start_character_analysis(episode_id: str, payload: StartCharacterAnalysisRequest):
    return {
        "success": True,
        "data": {
            "episode_id": episode_id,
            "stage_name": "character_analysis",
            "state": "needs_review",
            "source_video": payload.source_video,
        },
    }


@router.post("/episodes/{episode_id}/analysis/character/approve")
def approve_character_analysis(episode_id: str, payload: ApproveCharacterAnalysisRequest):
    return {
        "success": True,
        "data": {
            "episode_id": episode_id,
            "state": "approved",
            "approved_characters": [item.model_dump() for item in payload.approved_characters],
        },
    }
