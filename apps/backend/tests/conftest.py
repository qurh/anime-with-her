import pytest
from fastapi.testclient import TestClient

from app.api.routes.jobs import job_store
from app.main import app


@pytest.fixture(autouse=True)
def reset_job_store():
    job_store.reset()
    yield
    job_store.reset()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
