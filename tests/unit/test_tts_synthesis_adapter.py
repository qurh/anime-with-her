import json
from pathlib import Path

from worker.adapters.tts_synthesis import run_tts_synthesis


def test_tts_synthesis_builds_expected_contract_and_artifacts(tmp_path: Path):
    result = run_tts_synthesis(
        episode_id="episode_1",
        dub_segments=[
            {"segment_id": "seg_1", "dub_text": "你好", "duration_target_ms": 1100, "style_hint": "温柔"},
            {"segment_id": "seg_2", "dub_text": "谢谢", "duration_target_ms": 900, "style_hint": "坚定"},
        ],
        root=str(tmp_path / "episodes"),
    )

    assert result["stage_name"] == "tts_synthesis"
    assert result["state"] == "success"
    assert result["input_refs"] == ["in_memory:dub_segments"]
    assert result["output_refs"][0].endswith("/episodes/episode_1/generation/tts_segments/manifest.json")
    assert result["artifacts"]["manifest_path"].endswith("/episodes/episode_1/generation/tts_segments/manifest.json")
    assert len(result["artifacts"]["segments"]) == 2
    assert result["artifacts"]["segments"][0]["audio_path"].endswith(
        "/episodes/episode_1/generation/tts_segments/seg_1.wav"
    )
    assert result["artifacts"]["segments"][0]["provider"] in {"aliyun_tts", "doubao_tts"}

    manifest_path = Path(result["artifacts"]["manifest_path"])
    assert manifest_path.exists()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_data[0]["segment_id"] == "seg_1"
    assert Path(manifest_data[0]["audio_path"]).exists()
