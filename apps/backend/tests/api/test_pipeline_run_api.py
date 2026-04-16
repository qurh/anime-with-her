def test_run_episode_pipeline_returns_run_id(client, tmp_path):
    response = client.post(
        "/api/v1/episodes/episode_1/pipeline/run",
        json={
            "source_video": "data/input/demo.mkv",
            "root": str(tmp_path / "episodes"),
        },
    )

    assert response.status_code == 202
    payload = response.json()["data"]
    assert payload["run_id"].startswith("run_")
    assert payload["episode_id"] == "episode_1"
    assert payload["state"] == "pending"


def test_run_episode_pipeline_accepts_start_stage(client, tmp_path, monkeypatch):
    captured: dict[str, str | None] = {}

    def fake_runner(*, episode_id: str, source_video: str, root: str, start_stage: str | None = None):
        captured["start_stage"] = start_stage
        return {
            "state": "success",
            "stages": [],
            "stage_results": {},
            "outputs": {
                "final_audio_path": str(tmp_path / "final.wav"),
                "final_video_path": str(tmp_path / "final.mp4"),
            },
        }

    monkeypatch.setattr("app.api.routes.pipeline._load_episode_runner", lambda: fake_runner)

    response = client.post(
        "/api/v1/episodes/episode_1/pipeline/run",
        json={
            "source_video": "data/input/demo.mkv",
            "root": str(tmp_path / "episodes"),
            "start_stage": "tts_synthesis",
        },
    )

    assert response.status_code == 202
    assert captured["start_stage"] == "tts_synthesis"
