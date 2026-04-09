import pytest


def test_job_state_transitions_allow_happy_path():
    from app.domain.job import JobState, can_transition

    assert can_transition(JobState.CREATED, JobState.RUNNING) is True


def test_job_state_transitions_allow_budget_pause_and_resume():
    from app.domain.job import JobState, can_transition

    assert can_transition(JobState.RUNNING, JobState.AWAITING_BUDGET_DECISION) is True
    assert can_transition(JobState.AWAITING_BUDGET_DECISION, JobState.RUNNING) is True


def test_job_state_transitions_allow_rerender_after_partial_done():
    from app.domain.job import JobState, can_transition

    assert can_transition(JobState.PARTIAL_DONE, JobState.RERENDERING) is True


def test_job_state_transitions_block_terminal_resume():
    from app.domain.job import JobState, can_transition

    assert can_transition(JobState.DONE, JobState.RUNNING) is False
    assert can_transition(JobState.FAILED, JobState.RUNNING) is False


def test_create_session_rejects_non_sqlite_dsn():
    from app.db.session import create_session

    with pytest.raises(ValueError):
        create_session("postgresql://localhost/db")
