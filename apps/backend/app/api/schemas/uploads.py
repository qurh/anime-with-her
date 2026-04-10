from pydantic import BaseModel


class VideoUploadData(BaseModel):
    stored_path: str
    original_filename: str
    size_bytes: int
    content_type: str


class VideoUploadResponse(BaseModel):
    success: bool = True
    data: VideoUploadData
