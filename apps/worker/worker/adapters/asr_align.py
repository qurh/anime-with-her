import json
from pathlib import Path

from worker.config import asr_runtime_env_ready, load_worker_config
from worker.manifest import build_stage_manifest


def _asr_runtime_ready() -> bool:
    return asr_runtime_env_ready()


def _run_fake_asr(segments_path: Path) -> list[dict[str, object]]:
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
    return segments


def _run_real_asr(episode_id: str, vocals_path: str, segments_path: Path) -> list[dict[str, object]]:
    raise NotImplementedError("real asr runner is not implemented")


def run_asr_align(
    episode_id: str,
    vocals_path: str,
    root: str = "data/episodes",
) -> dict[str, object]:
    config = load_worker_config()
    wants_real = config.should_use_real("asr_align")

    asr_dir = Path(root) / episode_id / "analysis" / "asr_align"
    asr_dir.mkdir(parents=True, exist_ok=True)

    segments_path = asr_dir / "segments.json"
    warnings: list[str] = []
    execution_mode = "fake"

    if wants_real:
        if _asr_runtime_ready():
            try:
                segments = _run_real_asr(
                    episode_id=episode_id,
                    vocals_path=vocals_path,
                    segments_path=segments_path,
                )
                execution_mode = "real"
            except Exception as error:
                warnings.append(f"asr execution failed, fallback to fake align: {error}")
                segments = _run_fake_asr(segments_path)
        else:
            warnings.append("asr runtime unavailable, fallback to fake align")
            segments = _run_fake_asr(segments_path)
    else:
        segments = _run_fake_asr(segments_path)

    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="asr_align",
        state="success",
        input_refs=[vocals_path],
        output_refs=[segments_path.as_posix()],
    )

    return {
        **manifest,
        "execution_mode": execution_mode,
        "warnings": warnings,
        "artifacts": {
            "segments_path": segments_path.as_posix(),
            "segments": segments,
        },
    }
