import json
from pathlib import Path

from worker.manifest import build_stage_manifest


def run_asr_align(
    episode_id: str,
    vocals_path: str,
    root: str = "data/episodes",
) -> dict[str, object]:
    asr_dir = Path(root) / episode_id / "analysis" / "asr_align"
    asr_dir.mkdir(parents=True, exist_ok=True)

    segments_path = asr_dir / "segments.json"
    segments = [
        {
            "segment_id": "seg_1",
            "speaker_id": "spk_1",
            "start_ms": 0,
            "end_ms": 1200,
            "source_text": "placeholder source text",
        }
    ]
    segments_path.write_text(json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="asr_align",
        state="success",
        input_refs=[vocals_path],
        output_refs=[segments_path.as_posix()],
    )

    return {
        **manifest,
        "artifacts": {
            "segments_path": segments_path.as_posix(),
            "segments": segments,
        },
    }
