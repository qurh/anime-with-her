from fastapi import APIRouter

from app.api.schemas.budget import BudgetDecisionData, BudgetDecisionResponse
from app.services.budget_service import get_budget_decision

router = APIRouter()


@router.get("/jobs/{job_id}/budget-decision", response_model=BudgetDecisionResponse)
def budget_decision(job_id: str):
    result = get_budget_decision(job_id)
    return {"success": True, "data": BudgetDecisionData(**result)}
