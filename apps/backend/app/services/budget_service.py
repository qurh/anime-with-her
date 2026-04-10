from __future__ import annotations

from app.domain.budget import DEFAULT_TIMEOUT_ACTION, DEFAULT_WAIT_ACTION, TIMEOUT_MINUTES


def resolve_timeout_action(waited_minutes: int) -> str:
    if waited_minutes >= TIMEOUT_MINUTES:
        return DEFAULT_TIMEOUT_ACTION
    return DEFAULT_WAIT_ACTION


def get_budget_decision(job_id: str) -> dict[str, object]:
    return {
        "job_id": job_id,
        "options": ["skip_lipsync_continue_dubbing", "continue_full_pipeline"],
        "estimated_extra_cost_cny": 1.25,
        "timeout_minutes": TIMEOUT_MINUTES,
        "default_action": DEFAULT_TIMEOUT_ACTION,
    }
