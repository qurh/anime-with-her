import json
import os
from pathlib import Path

from worker.config import load_worker_config
from worker.manifest import build_stage_manifest

_TRUE_VALUES = {"1", "true", "yes", "on"}


def _diarization_runtime_ready() -> bool:
    if os.getenv("DIARIZATION_RUNTIME_READY", "").strip().lower() in _TRUE_VALUES:
        return True
    return any(
        os.getenv(env_name, "").strip()
        for env_name in ("DIARIZATION_MODEL_PATH", "SPEAKER_ROLE_MODEL_PATH", "PYANNOTE_TOKEN")
    )


def _run_fake_diarization() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
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
    return speaker_segments, speakers


def _run_real_diarization(
    episode_id: str,
    segments_path: str,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    _ = (episode_id, segments_path)
    raise NotImplementedError("real speaker role runner is not implemented")


def run_speaker_role(
    episode_id: str,
    segments_path: str,
    root: str = "data/episodes",
) -> dict[str, object]:
    config = load_worker_config()
    wants_real = config.should_use_real("speaker_role")

    speaker_role_dir = Path(root) / episode_id / "analysis" / "speaker_role"
    speaker_role_dir.mkdir(parents=True, exist_ok=True)

    speaker_segments_path = speaker_role_dir / "speaker_segments.json"
    speakers_path = speaker_role_dir / "speakers.json"

    warnings: list[str] = []
    execution_mode = "fake"
    if wants_real:
        if _diarization_runtime_ready():
            try:
                speaker_segments, speakers = _run_real_diarization(
                    episode_id=episode_id,
                    segments_path=segments_path,
                )
                execution_mode = "real"
            except Exception as error:
                warnings.append(f"speaker role execution failed, fallback to fake diarization: {error}")
                speaker_segments, speakers = _run_fake_diarization()
        else:
            warnings.append("speaker role runtime unavailable, fallback to fake diarization")
            speaker_segments, speakers = _run_fake_diarization()
    else:
        speaker_segments, speakers = _run_fake_diarization()

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
        "execution_mode": execution_mode,
        "warnings": warnings,
        "artifacts": {
            "speaker_segments_path": speaker_segments_path.as_posix(),
            "speakers_path": speakers_path.as_posix(),
            "speaker_segments": speaker_segments,
            "speakers": speakers,
        },
    }
