from pathlib import Path


def test_run_episode_pipeline_returns_success(client, tmp_path):
    response = client.post(
        "/api/v1/episodes/episode_1/pipeline/run",
        json={
            "source_video": "data/input/demo.mkv",
            "root": str(tmp_path / "episodes"),
        },
    )

    assert response.status_code == 202
    payload = response.json()["data"]
    assert payload["episode_id"] == "episode_1"
    assert payload["state"] == "success"
    assert payload["stages"] == [
        "media_ingest",
        "audio_separation",
        "asr_align",
        "speaker_role",
        "dub_script",
        "tts_synthesis",
        "mix_master",
    ]
    assert payload["stage_states"]["mix_master"] == "success"
    assert Path(payload["final_audio_path"]).exists()
    assert Path(payload["final_video_path"]).exists()
