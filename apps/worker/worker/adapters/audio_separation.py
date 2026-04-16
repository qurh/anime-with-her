from pathlib import Path

from worker.manifest import build_stage_manifest


def run_audio_separation(
    episode_id: str,
    normalized_vocals_path: str,
    root: str = "data/episodes",
) -> dict[str, object]:
    separation_dir = Path(root) / episode_id / "analysis" / "separation"
    separation_dir.mkdir(parents=True, exist_ok=True)

    vocals_path = separation_dir / "vocals.wav"
    background_path = separation_dir / "background.wav"
    effects_path = separation_dir / "effects.wav"

    vocals_path.write_text("placeholder separated vocals\n", encoding="utf-8")
    background_path.write_text("placeholder separated background\n", encoding="utf-8")
    effects_path.write_text("placeholder separated effects\n", encoding="utf-8")

    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="audio_separation",
        state="success",
        input_refs=[normalized_vocals_path],
        output_refs=[
            vocals_path.as_posix(),
            background_path.as_posix(),
            effects_path.as_posix(),
        ],
    )

    return {
        **manifest,
        "artifacts": {
            "vocals_path": vocals_path.as_posix(),
            "background_path": background_path.as_posix(),
            "effects_path": effects_path.as_posix(),
        },
    }
