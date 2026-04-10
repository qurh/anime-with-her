from pydantic import BaseModel


class CreateVoiceVersionRequest(BaseModel):
    series: str
    character: str
    sample_path: str


class VoiceVersionData(BaseModel):
    version_id: str
    status: str


class VoiceVersionResponse(BaseModel):
    success: bool = True
    data: VoiceVersionData
