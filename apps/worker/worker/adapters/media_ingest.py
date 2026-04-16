import shutil
import subprocess
from pathlib import Path

from worker.config import load_worker_config
from worker.manifest import build_stage_manifest


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _run_ffmpeg_extract_normalize(source_video: str, output_wav_path: Path):
    command = [
        "ffmpeg",
        "-y",
        "-i",
        source_video,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        output_wav_path.as_posix(),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def run_media_ingest(episode_id: str, source_video: str, root: str = "data/episodes") -> dict[str, object]:
    config = load_worker_config()
    wants_real = config.should_use_real("media_ingest")

    episode_dir = Path(root) / episode_id
    input_dir = episode_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(source_video).suffix or ".mp4"
    source_video_path = input_dir / f"source{suffix}"
    normalized_vocals_path = input_dir / "vocals_norm.wav"

    warnings: list[str] = []
    source_candidate = Path(source_video)
    if source_candidate.exists():
        shutil.copyfile(source_candidate, source_video_path)
    else:
        source_video_path.write_text(f"placeholder for {source_video}\n", encoding="utf-8")

    execution_mode = "fake"
    if wants_real:
        if _ffmpeg_available() and source_candidate.exists():
            try:
                _run_ffmpeg_extract_normalize(source_video, normalized_vocals_path)
                execution_mode = "real"
            except Exception as error:
                warnings.append(f"ffmpeg execution failed, fallback to fake ingest: {error}")
        else:
            warnings.append("ffmpeg unavailable or source video missing, fallback to fake ingest")

    if execution_mode == "fake":
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
        "warnings": warnings,
        "artifacts": {
            "source_video_path": source_video_path.as_posix(),
            "normalized_vocals_path": normalized_vocals_path.as_posix(),
        },
    }
