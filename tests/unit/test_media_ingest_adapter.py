from pathlib import Path

from worker.adapters.media_ingest import run_media_ingest


def test_media_ingest_builds_expected_contract_and_artifacts(tmp_path: Path):
    result = run_media_ingest(
        episode_id="episode_1",
        source_video="data/input/demo.mkv",
        root=str(tmp_path / "episodes"),
    )

    assert result["stage_name"] == "media_ingest"
    assert result["state"] == "success"
    assert result["input_refs"] == ["data/input/demo.mkv"]
    assert result["output_refs"][0].endswith("/episodes/episode_1/input/source.mkv")
    assert result["output_refs"][1].endswith("/episodes/episode_1/input/vocals_norm.wav")
    assert result["artifacts"]["source_video_path"].endswith("/episodes/episode_1/input/source.mkv")
    assert result["artifacts"]["normalized_vocals_path"].endswith("/episodes/episode_1/input/vocals_norm.wav")

    assert Path(result["artifacts"]["source_video_path"]).exists()
    assert Path(result["artifacts"]["normalized_vocals_path"]).exists()
