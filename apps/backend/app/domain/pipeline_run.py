from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class PipelineRunState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class PipelineRun(BaseModel):
    run_id: str
    episode_id: str
    source_video: str
    root: str
    state: PipelineRunState = PipelineRunState.PENDING
    stage_states: dict[str, str] = Field(default_factory=dict)
    outputs: dict[str, str] = Field(default_factory=dict)
    qa_summary: dict[str, object] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    estimated_cost_cny: float = 0.0
    estimated_duration_seconds: int = 0
    cost_summary: dict[str, float | int] = Field(default_factory=dict)
    failed_stage: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
