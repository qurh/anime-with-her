import json
from pathlib import Path

from worker.adapters.mix_master import run_mix_master


def test_mix_master_builds_expected_contract_and_artifacts(tmp_path: Path):
    tts_manifest_path = tmp_path / "episodes" / "episode_1" / "generation" / "tts_segments" / "manifest.json"
    tts_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    tts_manifest_path.write_text(
        json.dumps([{"segment_id": "seg_1", "audio_path": "fake/seg_1.wav"}], ensure_ascii=False),
        encoding="utf-8",
    )

    result = run_mix_master(
        episode_id="episode_1",
        vocals_path="data/episodes/episode_1/analysis/separation/vocals.wav",
        background_path="data/episodes/episode_1/analysis/separation/background.wav",
        effects_path="data/episodes/episode_1/analysis/separation/effects.wav",
        tts_manifest_path=str(tts_manifest_path),
        root=str(tmp_path / "episodes"),
    )

    assert result["stage_name"] == "mix_master"
    assert result["state"] == "success"
    assert result["input_refs"][0].endswith("/analysis/separation/vocals.wav")
    assert result["input_refs"][1].endswith("/analysis/separation/background.wav")
    assert result["input_refs"][2].endswith("/analysis/separation/effects.wav")
    assert result["output_refs"][0].endswith("/episodes/episode_1/output/final_audio_mix.wav")
    assert result["output_refs"][1].endswith("/episodes/episode_1/output/final_dubbed.mp4")
    assert result["artifacts"]["final_audio_path"].endswith("/episodes/episode_1/output/final_audio_mix.wav")
    assert result["artifacts"]["final_video_path"].endswith("/episodes/episode_1/output/final_dubbed.mp4")

    assert Path(result["artifacts"]["final_audio_path"]).exists()
    assert Path(result["artifacts"]["final_video_path"]).exists()
