from fastapi import APIRouter

from app.api.schemas.voice_registry import (
    CreateVoiceVersionRequest,
    VoiceVersionData,
    VoiceVersionResponse,
)
from app.services.voice_registry_service import create_voice_profile_version

router = APIRouter()


@router.post("/voice-registry/versions", status_code=201, response_model=VoiceVersionResponse)
def create_version(payload: CreateVoiceVersionRequest):
    result = create_voice_profile_version(payload)
    return {"success": True, "data": VoiceVersionData(**result)}
