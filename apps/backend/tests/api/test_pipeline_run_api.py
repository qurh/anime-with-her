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
