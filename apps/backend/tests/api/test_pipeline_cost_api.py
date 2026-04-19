import time


def _wait_for_terminal_state(client, run_id: str, timeout_seconds: float = 5.0):
    deadline = time.time() + timeout_seconds
    latest_payload = None
    while time.time() < deadline:
        response = client.get(f"/api/v1/pipeline-runs/{run_id}")
        assert response.status_code == 200
        latest_payload = response.json()["data"]
        if latest_payload["state"] in {"success", "failed"}:
            return latest_payload
        time.sleep(0.05)
    return latest_payload


def test_pipeline_run_trigger_returns_cost_estimate(client, tmp_path):
    response = client.post(
        "/api/v1/episodes/episode_cost_1/pipeline/run",
        json={
            "source_video": "data/input/demo.mkv",
            "root": str(tmp_path / "episodes"),
        },
    )
    assert response.status_code == 202
    payload = response.json()["data"]
    assert payload["estimated_cost_cny"] > 0
    assert payload["estimated_duration_seconds"] > 0


def test_pipeline_run_status_returns_cost_summary(client, tmp_path):
    trigger = client.post(
        "/api/v1/episodes/episode_cost_2/pipeline/run",
        json={
            "source_video": "data/input/demo.mkv",
            "root": str(tmp_path / "episodes"),
        },
    )
    assert trigger.status_code == 202
    run_id = trigger.json()["data"]["run_id"]

    status_payload = _wait_for_terminal_state(client, run_id)
    assert status_payload is not None
    assert status_payload["cost_summary"]["estimated_cost_cny"] > 0
    assert status_payload["cost_summary"]["actual_cost_cny"] >= 0
    assert isinstance(status_payload["qa_summary"], dict)
    assert isinstance(status_payload["warnings"], list)
