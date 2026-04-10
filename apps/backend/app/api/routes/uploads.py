from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request

from app.api.schemas.uploads import VideoUploadData, VideoUploadResponse
from app.services.upload_service import save_uploaded_video

router = APIRouter()


@router.post("/uploads/video", response_model=VideoUploadResponse)
async def upload_video(
    request: Request,
    x_filename: str | None = Header(default=None),
):
    content_type = request.headers.get("content-type", "")
    if not (content_type.startswith("video/") or content_type == "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Only video file uploads are supported.")

    body = await request.body()
    if not body:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        result = save_uploaded_video(body, x_filename, content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"success": True, "data": VideoUploadData(**result)}
