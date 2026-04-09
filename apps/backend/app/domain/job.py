from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class JobState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PARTIAL_DONE = "partial_done"
    DONE = "done"
    FAILED = "failed"
    AWAITING_BUDGET_DECISION = "awaiting_budget_decision"
    RERENDERING = "rerendering"


_ALLOWED_TRANSITIONS: Final[dict[JobState, set[JobState]]] = {
    JobState.CREATED: {JobState.RUNNING, JobState.FAILED},
    JobState.RUNNING: {
        JobState.PARTIAL_DONE,
        JobState.DONE,
        JobState.FAILED,
        JobState.AWAITING_BUDGET_DECISION,
    },
    JobState.PARTIAL_DONE: {JobState.DONE, JobState.FAILED, JobState.RERENDERING},
    JobState.DONE: set(),
    JobState.FAILED: set(),
    JobState.AWAITING_BUDGET_DECISION: {JobState.RUNNING, JobState.FAILED},
    JobState.RERENDERING: {JobState.RUNNING, JobState.FAILED},
}


@dataclass(slots=True)
class Job:
    job_id: str
    input_video: str | None = None
    state: JobState = JobState.CREATED


def can_transition(src: JobState, dst: JobState) -> bool:
    return dst in _ALLOWED_TRANSITIONS.get(src, set())
