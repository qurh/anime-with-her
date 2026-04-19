import json
from pathlib import Path

from worker.adapters.tts_provider import TtsProviderRouter, build_default_tts_router
from worker.manifest import build_stage_manifest


def run_tts_synthesis(
    episode_id: str,
    dub_segments: list[dict[str, object]],
    root: str = "data/episodes",
    provider_router: TtsProviderRouter | None = None,
) -> dict[str, object]:
    router = provider_router or build_default_tts_router()
    tts_dir = Path(root) / episode_id / "generation" / "tts_segments"
    tts_dir.mkdir(parents=True, exist_ok=True)

    rendered_segments: list[dict[str, object]] = []
    for segment in dub_segments:
        segment_id = str(segment["segment_id"])
        dub_text = str(segment["dub_text"])
        duration_target_ms = int(segment["duration_target_ms"])
        style_hint_value = segment.get("style_hint", "")
        style_hint = "" if style_hint_value is None else str(style_hint_value)

        tts_result = router.synthesize(
            text=dub_text,
            duration_ms=duration_target_ms,
            style_hint=style_hint,
        )

        audio_path = tts_dir / f"{segment_id}.wav"
        audio_path.write_text(tts_result["audio_payload"], encoding="utf-8")
        rendered_segments.append(
            {
                "segment_id": segment_id,
                "audio_path": audio_path.as_posix(),
                "provider": tts_result["provider"],
                "duration_target_ms": duration_target_ms,
            }
        )

    manifest_path = tts_dir / "manifest.json"
    manifest_path.write_text(json.dumps(rendered_segments, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="tts_synthesis",
        state="success",
        input_refs=["in_memory:dub_segments"],
        output_refs=[manifest_path.as_posix()],
    )

    return {
        **manifest,
        "artifacts": {
            "manifest_path": manifest_path.as_posix(),
            "segments": rendered_segments,
        },
    }
