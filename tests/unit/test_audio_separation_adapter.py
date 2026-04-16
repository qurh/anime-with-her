from pathlib import Path

from worker.adapters.audio_separation import run_audio_separation


def test_audio_separation_builds_expected_contract_and_artifacts(tmp_path: Path):
    result = run_audio_separation(
        episode_id="episode_1",
        normalized_vocals_path="data/episodes/episode_1/input/vocals_norm.wav",
        root=str(tmp_path / "episodes"),
    )

    assert result["stage_name"] == "audio_separation"
    assert result["state"] == "success"
    assert result["input_refs"] == ["data/episodes/episode_1/input/vocals_norm.wav"]
    assert result["output_refs"][0].endswith("/episodes/episode_1/analysis/separation/vocals.wav")
    assert result["output_refs"][1].endswith("/episodes/episode_1/analysis/separation/background.wav")
    assert result["output_refs"][2].endswith("/episodes/episode_1/analysis/separation/effects.wav")
    assert result["artifacts"]["vocals_path"].endswith("/episodes/episode_1/analysis/separation/vocals.wav")
    assert result["artifacts"]["background_path"].endswith(
        "/episodes/episode_1/analysis/separation/background.wav"
    )
    assert result["artifacts"]["effects_path"].endswith("/episodes/episode_1/analysis/separation/effects.wav")

    assert Path(result["artifacts"]["vocals_path"]).exists()
    assert Path(result["artifacts"]["background_path"]).exists()
    assert Path(result["artifacts"]["effects_path"]).exists()
