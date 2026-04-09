from __future__ import annotations

from pydantic import BaseModel

from app.domain.job import JobState


class CreateJobRequest(BaseModel):
    input_video: str | None = None


class JobData(BaseModel):
    job_id: str
    state: JobState
    input_video: str | None = None


class JobResponse(BaseModel):
    success: bool = True
    data: JobData