from pathlib import Path

from worker.config import load_worker_config
from worker.manifest import build_stage_manifest


def run_media_ingest(episode_id: str, source_video: str, root: str = "data/episodes") -> dict[str, object]:
    config = load_worker_config()
    execution_mode = "real" if config.should_use_real("media_ingest") else "fake"

    episode_dir = Path(root) / episode_id
    input_dir = episode_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(source_video).suffix or ".mp4"
    source_video_path = input_dir / f"source{suffix}"
    normalized_vocals_path = input_dir / "vocals_norm.wav"

    source_video_path.write_text(f"placeholder for {source_video}\n", encoding="utf-8")
    normalized_vocals_path.write_text("placeholder normalized vocals\n", encoding="utf-8")

    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="media_ingest",
        state="success",
        input_refs=[source_video],
        output_refs=[source_video_path.as_posix(), normalized_vocals_path.as_posix()],
    )

    return {
        **manifest,
        "execution_mode": execution_mode,
        "artifacts": {
            "source_video_path": source_video_path.as_posix(),
            "normalized_vocals_path": normalized_vocals_path.as_posix(),
        },
    }
