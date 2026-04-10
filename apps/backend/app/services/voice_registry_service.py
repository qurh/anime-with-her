from app.api.schemas.voice_registry import CreateVoiceVersionRequest


def create_voice_profile_version(payload: CreateVoiceVersionRequest) -> dict[str, str]:
    _ = payload
    return {"version_id": "v1", "status": "auto_collected"}
