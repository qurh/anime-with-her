from __future__ import annotations

from threading import Lock

from fastapi import APIRouter, HTTPException

from app.api.schemas.jobs import CreateJobRequest, JobData, JobResponse
from app.domain.job import Job, JobState

router = APIRouter()


class JobStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._jobs: dict[str, Job] = {}
        self._next_job_number = 1

    def create(self, input_video: str | None) -> Job:
        with self._lock:
            job_id = f"job_{self._next_job_number}"
            self._next_job_number += 1
            job = Job(job_id=job_id, input_video=input_video, state=JobState.CREATED)
            self._jobs[job_id] = job
            return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update_state(self, job_id: str, state: JobState) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.state = state

    def reset(self) -> None:
        with self._lock:
            self._jobs.clear()
            self._next_job_number = 1


job_store = JobStore()


@router.post("/jobs", status_code=201, response_model=JobResponse)
def create_job(payload: CreateJobRequest):
    job = job_store.create(payload.input_video)

    return {
        "success": True,
        "data": JobData(job_id=job.job_id, state=job.state, input_video=job.input_video),
    }


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    current_state = job.state
    if job.state == JobState.CREATED:
        job_store.update_state(job_id, JobState.RUNNING)

    return {
        "success": True,
        "data": JobData(job_id=job.job_id, state=current_state, input_video=job.input_video),
    }
