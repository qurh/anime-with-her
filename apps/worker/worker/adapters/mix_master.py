from pathlib import Path

from worker.manifest import build_stage_manifest


def run_mix_master(
    episode_id: str,
    vocals_path: str,
    background_path: str,
    effects_path: str,
    tts_manifest_path: str,
    root: str = "data/episodes",
) -> dict[str, object]:
    output_dir = Path(root) / episode_id / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    final_audio_path = output_dir / "final_audio_mix.wav"
    final_video_path = output_dir / "final_dubbed.mp4"

    final_audio_path.write_text(
        f"mix placeholder\nvocals={vocals_path}\nbgm={background_path}\neffects={effects_path}\ntts={tts_manifest_path}\n",
        encoding="utf-8",
    )
    final_video_path.write_text("video placeholder with dubbed audio\n", encoding="utf-8")

    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="mix_master",
        state="success",
        input_refs=[vocals_path, background_path, effects_path, tts_manifest_path],
        output_refs=[final_audio_path.as_posix(), final_video_path.as_posix()],
    )

    return {
        **manifest,
        "artifacts": {
            "final_audio_path": final_audio_path.as_posix(),
            "final_video_path": final_video_path.as_posix(),
        },
    }
