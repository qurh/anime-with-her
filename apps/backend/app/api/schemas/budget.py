from pydantic import BaseModel


class BudgetDecisionData(BaseModel):
    job_id: str
    options: list[str]
    estimated_extra_cost_cny: float
    timeout_minutes: int
    default_action: str


class BudgetDecisionResponse(BaseModel):
    success: bool = True
    data: BudgetDecisionData
