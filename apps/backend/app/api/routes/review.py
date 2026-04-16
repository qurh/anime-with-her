from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RegenerateSegmentRequest(BaseModel):
    dub_text: str
    emotion: str
    reference_sample_id: str


@router.post("/episodes/{episode_id}/segments/{segment_id}/regenerate", status_code=202)
def regenerate_segment(episode_id: str, segment_id: str, payload: RegenerateSegmentRequest):
    return {
        "success": True,
        "data": {
            "episode_id": episode_id,
            "segment_id": segment_id,
            "state": "running",
            "dub_text": payload.dub_text,
            "emotion": payload.emotion,
            "reference_sample_id": payload.reference_sample_id,
        },
    }
