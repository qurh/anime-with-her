import json
from pathlib import Path

from worker.manifest import build_stage_manifest


def run_speaker_role(
    episode_id: str,
    segments_path: str,
    root: str = "data/episodes",
) -> dict[str, object]:
    speaker_role_dir = Path(root) / episode_id / "analysis" / "speaker_role"
    speaker_role_dir.mkdir(parents=True, exist_ok=True)

    speaker_segments_path = speaker_role_dir / "speaker_segments.json"
    speakers_path = speaker_role_dir / "speakers.json"

    speaker_segments = [
        {
            "segment_id": "seg_1",
            "speaker_id": "spk_1",
            "start_ms": 0,
            "end_ms": 1200,
        }
    ]
    speakers = [
        {
            "speaker_id": "spk_1",
            "role_candidate_id": "candidate_1",
            "confidence": 0.9,
        }
    ]

    speaker_segments_path.write_text(
        json.dumps(speaker_segments, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    speakers_path.write_text(
        json.dumps(speakers, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="speaker_role",
        state="success",
        input_refs=[segments_path],
        output_refs=[speaker_segments_path.as_posix(), speakers_path.as_posix()],
    )

    return {
        **manifest,
        "artifacts": {
            "speaker_segments_path": speaker_segments_path.as_posix(),
            "speakers_path": speakers_path.as_posix(),
            "speaker_segments": speaker_segments,
            "speakers": speakers,
        },
    }
