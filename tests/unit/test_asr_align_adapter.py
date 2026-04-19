import json
from pathlib import Path

from worker.adapters.asr_align import run_asr_align


def test_asr_align_builds_expected_contract_and_artifacts(tmp_path: Path):
    result = run_asr_align(
        episode_id="episode_1",
        vocals_path="data/episodes/episode_1/analysis/separation/vocals.wav",
        root=str(tmp_path / "episodes"),
    )

    assert result["stage_name"] == "asr_align"
    assert result["state"] == "success"
    assert result["input_refs"] == ["data/episodes/episode_1/analysis/separation/vocals.wav"]
    assert result["output_refs"][0].endswith("/episodes/episode_1/analysis/asr_align/segments.json")
    assert result["execution_mode"] == "fake"
    assert result["warnings"] == []
    assert result["artifacts"]["segments_path"].endswith("/episodes/episode_1/analysis/asr_align/segments.json")
    assert result["artifacts"]["segments"][0]["segment_id"] == "seg_1"
    assert result["artifacts"]["segments"][0]["source_text"]

    segments_path = Path(result["artifacts"]["segments_path"])
    assert segments_path.exists()
    segments = json.loads(segments_path.read_text(encoding="utf-8"))
    assert segments[0]["segment_id"] == "seg_1"
