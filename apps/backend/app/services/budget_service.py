from __future__ import annotations

from app.domain.budget import DEFAULT_TIMEOUT_ACTION, DEFAULT_WAIT_ACTION, TIMEOUT_MINUTES


def resolve_timeout_action(waited_minutes: int) -> str:
    if waited_minutes >= TIMEOUT_MINUTES:
        return DEFAULT_TIMEOUT_ACTION
    return DEFAULT_WAIT_ACTION
