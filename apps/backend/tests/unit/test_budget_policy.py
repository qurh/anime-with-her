from decimal import Decimal


def test_budget_cap_is_five_cny():
    from app.domain.budget import BUDGET_CAP_CNY

    assert isinstance(BUDGET_CAP_CNY, Decimal)
    assert BUDGET_CAP_CNY == Decimal("5")


def test_is_within_budget_below_cap():
    from app.domain.budget import is_within_budget

    assert is_within_budget(Decimal("4.99")) is True


def test_is_within_budget_at_cap():
    from app.domain.budget import is_within_budget

    assert is_within_budget(Decimal("5")) is True


def test_is_within_budget_above_cap():
    from app.domain.budget import is_within_budget

    assert is_within_budget(Decimal("5.01")) is False


def test_budget_timeout_defaults_to_skip_lipsync():
    from app.services.budget_service import resolve_timeout_action

    assert resolve_timeout_action(waited_minutes=10) == "skip_lipsync_continue_dubbing"


def test_budget_timeout_before_threshold_waits_for_user():
    from app.services.budget_service import resolve_timeout_action

    assert resolve_timeout_action(waited_minutes=9) == "await_user_choice"


def test_budget_timeout_at_threshold_skips_lipsync():
    from app.services.budget_service import resolve_timeout_action

    assert resolve_timeout_action(waited_minutes=10) == "skip_lipsync_continue_dubbing"


def test_budget_timeout_after_threshold_skips_lipsync():
    from app.services.budget_service import resolve_timeout_action

    assert resolve_timeout_action(waited_minutes=11) == "skip_lipsync_continue_dubbing"
