import json
from pathlib import Path

from worker.adapters.speaker_role import run_speaker_role


def test_speaker_role_builds_expected_contract_and_artifacts(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "fake")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)
    monkeypatch.delenv("DIARIZATION_RUNTIME_READY", raising=False)
    monkeypatch.delenv("DIARIZATION_MODEL_PATH", raising=False)
    monkeypatch.delenv("SPEAKER_ROLE_MODEL_PATH", raising=False)
    monkeypatch.delenv("PYANNOTE_TOKEN", raising=False)

    result = run_speaker_role(
        episode_id="episode_1",
        segments_path="data/episodes/episode_1/analysis/asr_align/segments.json",
        root=str(tmp_path / "episodes"),
    )

    assert result["stage_name"] == "speaker_role"
    assert result["state"] == "success"
    assert result["execution_mode"] == "fake"
    assert result["warnings"] == []
    assert result["input_refs"] == ["data/episodes/episode_1/analysis/asr_align/segments.json"]
    assert result["output_refs"][0].endswith("/episodes/episode_1/analysis/speaker_role/speaker_segments.json")
    assert result["output_refs"][1].endswith("/episodes/episode_1/analysis/speaker_role/speakers.json")
    assert result["artifacts"]["speaker_segments"][0]["segment_id"] == "seg_1"
    assert result["artifacts"]["speaker_segments"][0]["speaker_id"] == "spk_1"
    assert result["artifacts"]["speakers"][0]["speaker_id"] == "spk_1"
    assert result["artifacts"]["speakers"][0]["role_candidate_id"] == "candidate_1"

    speaker_segments_path = Path(result["artifacts"]["speaker_segments_path"])
    speakers_path = Path(result["artifacts"]["speakers_path"])
    assert speaker_segments_path.exists()
    assert speakers_path.exists()

    speaker_segments = json.loads(speaker_segments_path.read_text(encoding="utf-8"))
    speakers = json.loads(speakers_path.read_text(encoding="utf-8"))
    assert speaker_segments[0]["speaker_id"] == "spk_1"
    assert speakers[0]["role_candidate_id"] == "candidate_1"
