from __future__ import annotations

from decimal import Decimal

BUDGET_CAP_CNY = Decimal("5")
TIMEOUT_MINUTES = 10
DEFAULT_TIMEOUT_ACTION = "skip_lipsync_continue_dubbing"
DEFAULT_WAIT_ACTION = "await_user_choice"


def is_within_budget(estimated_cost_cny: Decimal) -> bool:
    return estimated_cost_cny <= BUDGET_CAP_CNY
