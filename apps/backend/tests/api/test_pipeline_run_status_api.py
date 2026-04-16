import time
from pathlib import Path


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


def test_pipeline_run_status_endpoint_returns_stage_states_and_outputs(client, tmp_path):
    trigger_response = client.post(
        "/api/v1/episodes/episode_status_1/pipeline/run",
        json={
            "source_video": "data/input/demo.mkv",
            "root": str(tmp_path / "episodes"),
        },
    )
    assert trigger_response.status_code == 202
    run_id = trigger_response.json()["data"]["run_id"]

    status_payload = _wait_for_terminal_state(client, run_id)
    assert status_payload is not None
    assert status_payload["state"] == "success"
    assert status_payload["stage_states"]["mix_master"] == "success"
    assert Path(status_payload["final_audio_path"]).exists()
    assert Path(status_payload["final_video_path"]).exists()


def test_episode_pipeline_runs_list_returns_latest_first(client, tmp_path):
    episode_id = "episode_list_case"
    first = client.post(
        f"/api/v1/episodes/{episode_id}/pipeline/run",
        json={
            "source_video": "data/input/a.mkv",
            "root": str(tmp_path / "episodes_a"),
        },
    )
    second = client.post(
        f"/api/v1/episodes/{episode_id}/pipeline/run",
        json={
            "source_video": "data/input/b.mkv",
            "root": str(tmp_path / "episodes_b"),
        },
    )
    assert first.status_code == 202
    assert second.status_code == 202

    run_id_1 = first.json()["data"]["run_id"]
    run_id_2 = second.json()["data"]["run_id"]

    list_response = client.get(f"/api/v1/episodes/{episode_id}/pipeline-runs")
    assert list_response.status_code == 200
    runs = list_response.json()["data"]
    assert [item["run_id"] for item in runs[:2]] == [run_id_2, run_id_1]
