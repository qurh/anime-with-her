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
    assert isinstance(status_payload["qa_summary"], dict)
    assert "timing_fit_score" in status_payload["qa_summary"]
    assert "voice_stability_score" in status_payload["qa_summary"]
    assert "mix_balance_score" in status_payload["qa_summary"]
    assert isinstance(status_payload["warnings"], list)
    assert all(isinstance(item, str) for item in status_payload["warnings"])
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


def test_pipeline_run_status_persists_exact_warning_content(client, tmp_path, monkeypatch):
    final_audio = tmp_path / "final.wav"
    final_video = tmp_path / "final.mp4"
    final_audio.write_text("audio", encoding="utf-8")
    final_video.write_text("video", encoding="utf-8")

    def fake_runner(*, episode_id: str, source_video: str, root: str, start_stage: str | None = None):
        _ = (episode_id, source_video, root, start_stage)
        return {
            "state": "success",
            "stages": ["media_ingest", "asr_align", "mix_master"],
            "stage_results": {
                "media_ingest": {
                    "state": "success",
                    "warnings": ["stage warning ingest"],
                },
                "asr_align": {
                    "state": "success",
                    "warnings": ["stage warning align"],
                },
                "mix_master": {
                    "state": "success",
                    "warnings": [],
                },
            },
            "warnings": ["top-level warning", "stage warning align"],
            "qa_summary": {
                "timing_fit_score": 0.9,
                "voice_stability_score": 0.91,
                "mix_balance_score": 0.92,
            },
            "outputs": {
                "final_audio_path": str(final_audio),
                "final_video_path": str(final_video),
            },
        }

    monkeypatch.setattr("app.api.routes.pipeline._load_episode_runner", lambda: fake_runner)

    trigger_response = client.post(
        "/api/v1/episodes/episode_warning_success/pipeline/run",
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
    assert status_payload["warnings"] == [
        "top-level warning",
        "stage warning align",
        "stage warning ingest",
    ]


def test_pipeline_run_status_failed_includes_meaningful_warnings(client, tmp_path, monkeypatch):
    def fake_runner(*, episode_id: str, source_video: str, root: str, start_stage: str | None = None):
        _ = (episode_id, source_video, root, start_stage)
        return {
            "state": "failed",
            "failed_stage": "asr_align",
            "error": "forced failure",
            "stages": ["media_ingest", "asr_align"],
            "stage_results": {
                "media_ingest": {
                    "state": "success",
                    "warnings": ["ingest warning"],
                },
                "asr_align": {
                    "state": "failed",
                    "warnings": ["align warning"],
                },
            },
            "warnings": "",
            "qa_summary": {},
            "outputs": {
                "final_audio_path": "",
                "final_video_path": "",
            },
        }

    monkeypatch.setattr("app.api.routes.pipeline._load_episode_runner", lambda: fake_runner)

    trigger_response = client.post(
        "/api/v1/episodes/episode_warning_failed/pipeline/run",
        json={
            "source_video": "data/input/demo.mkv",
            "root": str(tmp_path / "episodes"),
        },
    )
    assert trigger_response.status_code == 202
    run_id = trigger_response.json()["data"]["run_id"]

    status_payload = _wait_for_terminal_state(client, run_id)
    assert status_payload is not None
    assert status_payload["state"] == "failed"
    assert status_payload["warnings"] == ["ingest warning", "align warning"]
