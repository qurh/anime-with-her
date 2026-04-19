import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "worker"))

import worker.adapters.speaker_role as speaker_role_module


def test_speaker_role_real_mode_emits_speakers_and_segments(tmp_path: Path, monkeypatch):
    def _fake_real_diarization(episode_id: str, segments_path: str):
        assert episode_id == "episode_real_1"
        assert segments_path.endswith("/analysis/asr_align/segments.json")
        speaker_segments = [
            {
                "segment_id": "seg_real_1",
                "speaker_id": "spk_real_1",
                "start_ms": 100,
                "end_ms": 1600,
            }
        ]
        speakers = [
            {
                "speaker_id": "spk_real_1",
                "role_candidate_id": "candidate_real_1",
                "confidence": 0.95,
            }
        ]
        return speaker_segments, speakers

    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)
    monkeypatch.setattr(speaker_role_module, "_diarization_runtime_ready", lambda: True, raising=False)
    monkeypatch.setattr(speaker_role_module, "_run_real_diarization", _fake_real_diarization, raising=False)

    result = speaker_role_module.run_speaker_role(
        episode_id="episode_real_1",
        segments_path="data/episodes/episode_real_1/analysis/asr_align/segments.json",
        root=str(tmp_path / "episodes"),
    )

    assert result["execution_mode"] == "real"
    assert result["warnings"] == []
    assert result["artifacts"]["speaker_segments"][0]["segment_id"] == "seg_real_1"
    assert result["artifacts"]["speakers"][0]["role_candidate_id"] == "candidate_real_1"

    speaker_segments_path = Path(result["artifacts"]["speaker_segments_path"])
    speakers_path = Path(result["artifacts"]["speakers_path"])
    assert speaker_segments_path.exists()
    assert speakers_path.exists()


def test_speaker_role_real_mode_falls_back_when_runtime_unavailable(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)
    monkeypatch.setattr(speaker_role_module, "_diarization_runtime_ready", lambda: False, raising=False)

    result = speaker_role_module.run_speaker_role(
        episode_id="episode_real_2",
        segments_path="data/episodes/episode_real_2/analysis/asr_align/segments.json",
        root=str(tmp_path / "episodes"),
    )

    assert result["execution_mode"] == "fake"
    assert "runtime unavailable" in result["warnings"][0]
    assert result["artifacts"]["speaker_segments"][0]["segment_id"] == "seg_1"
    assert result["artifacts"]["speakers"][0]["role_candidate_id"] == "candidate_1"


def test_speaker_role_real_mode_falls_back_when_real_runner_raises(tmp_path: Path, monkeypatch):
    def _raise_real_diarization(episode_id: str, segments_path: str):
        raise RuntimeError("mock diarization crash")

    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)
    monkeypatch.setattr(speaker_role_module, "_diarization_runtime_ready", lambda: True, raising=False)
    monkeypatch.setattr(speaker_role_module, "_run_real_diarization", _raise_real_diarization, raising=False)

    result = speaker_role_module.run_speaker_role(
        episode_id="episode_real_3",
        segments_path="data/episodes/episode_real_3/analysis/asr_align/segments.json",
        root=str(tmp_path / "episodes"),
    )

    assert result["execution_mode"] == "fake"
    assert "fallback to fake diarization" in result["warnings"][0]
    assert "mock diarization crash" in result["warnings"][0]
    assert result["artifacts"]["speaker_segments"][0]["segment_id"] == "seg_1"
    assert result["artifacts"]["speakers"][0]["role_candidate_id"] == "candidate_1"
