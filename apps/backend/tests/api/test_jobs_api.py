from __future__ import annotations

import pytest

from app.api.routes.jobs import job_store
from app.api.schemas.jobs import JobData
from app.domain.job import JobState


@pytest.fixture(autouse=True)
def reset_job_store():
    job_store.reset()
    yield
    job_store.reset()


def test_job_data_state_uses_job_state_enum():
    data = JobData(job_id="job_1", state=JobState.CREATED)

    assert data.state is JobState.CREATED
    assert data.model_dump()["state"] == "created"


def test_create_job_returns_created_state(client):
    resp = client.post("/api/v1/jobs", json={"input_video": "data/input/a.mp4"})

    assert resp.status_code == 201
    body = resp.json()
    assert body["data"]["state"] == "created"


def test_get_job_returns_created_job(client):
    create_resp = client.post("/api/v1/jobs", json={"input_video": "data/input/a.mp4"})
    job_id = create_resp.json()["data"]["job_id"]

    resp = client.get(f"/api/v1/jobs/{job_id}")

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["job_id"] == job_id
    assert body["data"]["state"] == "created"