from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.job import JobState


@dataclass(slots=True)
class JobRecord:
    job_id: str
    input_video: str | None = None
    state: str = JobState.CREATED.value
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


JobModel = JobRecord
