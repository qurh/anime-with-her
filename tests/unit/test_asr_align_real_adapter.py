import json
from pathlib import Path

import worker.adapters.asr_align as asr_align_module


def test_asr_real_mode_uses_live_path_when_model_available(tmp_path: Path, monkeypatch):
    called: dict[str, str] = {}

    def _fake_real_asr(episode_id: str, vocals_path: str, segments_path: Path):
        called["episode_id"] = episode_id
        called["vocals_path"] = vocals_path
        called["segments_path"] = segments_path.as_posix()
        segments = [
            {
                "segment_id": "seg_real_1",
                "speaker_id": "spk_real_1",
                "start_ms": 10,
                "end_ms": 1180,
                "source_text": "live asr source text",
            }
        ]
        segments_path.write_text(json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8")
        return segments

    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)
    monkeypatch.setattr(asr_align_module, "_asr_runtime_ready", lambda: True, raising=False)
    monkeypatch.setattr(asr_align_module, "_run_real_asr", _fake_real_asr, raising=False)

    result = asr_align_module.run_asr_align(
        episode_id="episode_real_1",
        vocals_path="data/episodes/episode_real_1/analysis/separation/vocals.wav",
        root=str(tmp_path / "episodes"),
    )

    assert result["execution_mode"] == "real"
    assert result["warnings"] == []
    assert called["episode_id"] == "episode_real_1"
    assert called["vocals_path"] == "data/episodes/episode_real_1/analysis/separation/vocals.wav"
    assert called["segments_path"].endswith("/episodes/episode_real_1/analysis/asr_align/segments.json")

    segments_path = Path(result["artifacts"]["segments_path"])
    assert segments_path.exists()
    assert result["artifacts"]["segments"][0]["segment_id"] == "seg_real_1"
