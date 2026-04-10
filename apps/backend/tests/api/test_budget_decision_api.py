def test_budget_decision_payload_contains_two_options_and_estimate(client):
    resp = client.get("/api/v1/jobs/job_1/budget-decision")

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "skip_lipsync_continue_dubbing" in data["options"]
    assert "continue_full_pipeline" in data["options"]
    assert data["estimated_extra_cost_cny"] >= 0
