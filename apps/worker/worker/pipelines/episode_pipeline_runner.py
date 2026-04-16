from worker.adapters.asr_align import run_asr_align
from worker.adapters.audio_separation import run_audio_separation
from worker.adapters.media_ingest import run_media_ingest
from worker.adapters.mix_master import run_mix_master
from worker.adapters.speaker_role import run_speaker_role
from worker.adapters.tts_synthesis import run_tts_synthesis
from worker.pipelines.dub_script import rewrite_for_dubbing


def _build_dub_segments(asr_segments: list[dict[str, object]]) -> list[dict[str, object]]:
    dub_segments: list[dict[str, object]] = []
    for segment in asr_segments:
        start_ms = int(segment.get("start_ms", 0))
        end_ms = int(segment.get("end_ms", 0))
        duration_target_ms = max(1, end_ms - start_ms)
        source_text = str(segment.get("source_text", ""))
        literal_translation = source_text

        rewrite_result = rewrite_for_dubbing(
            source_text=source_text,
            literal_translation=literal_translation,
            character_style={"base_tone": "中性自然"},
            duration_ms=duration_target_ms,
        )

        dub_segments.append(
            {
                "segment_id": str(segment.get("segment_id", "seg_unknown")),
                "dub_text": rewrite_result["dub_text"],
                "duration_target_ms": rewrite_result["duration_target_ms"],
                "style_hint": rewrite_result["style_hint"],
                "provider": rewrite_result["provider"],
            }
        )
    return dub_segments


def run_episode_pipeline(episode_id: str, source_video: str, root: str = "data/episodes") -> dict[str, object]:
    media_ingest = run_media_ingest(episode_id=episode_id, source_video=source_video, root=root)
    audio_separation = run_audio_separation(
        episode_id=episode_id,
        normalized_vocals_path=str(media_ingest["artifacts"]["normalized_vocals_path"]),
        root=root,
    )
    asr_align = run_asr_align(
        episode_id=episode_id,
        vocals_path=str(audio_separation["artifacts"]["vocals_path"]),
        root=root,
    )
    speaker_role = run_speaker_role(
        episode_id=episode_id,
        segments_path=str(asr_align["artifacts"]["segments_path"]),
        root=root,
    )

    dub_segments = _build_dub_segments(asr_segments=list(asr_align["artifacts"]["segments"]))
    dub_script = {
        "stage_name": "dub_script",
        "state": "success",
        "segments": dub_segments,
    }

    tts_synthesis = run_tts_synthesis(
        episode_id=episode_id,
        dub_segments=dub_segments,
        root=root,
    )
    mix_master = run_mix_master(
        episode_id=episode_id,
        vocals_path=str(audio_separation["artifacts"]["vocals_path"]),
        background_path=str(audio_separation["artifacts"]["background_path"]),
        effects_path=str(audio_separation["artifacts"]["effects_path"]),
        tts_manifest_path=str(tts_synthesis["artifacts"]["manifest_path"]),
        root=root,
    )

    _ = speaker_role
    stage_results: dict[str, dict[str, object]] = {
        "media_ingest": media_ingest,
        "audio_separation": audio_separation,
        "asr_align": asr_align,
        "speaker_role": speaker_role,
        "dub_script": dub_script,
        "tts_synthesis": tts_synthesis,
        "mix_master": mix_master,
    }

    return {
        "episode_id": episode_id,
        "state": "success",
        "stages": [
            "media_ingest",
            "audio_separation",
            "asr_align",
            "speaker_role",
            "dub_script",
            "tts_synthesis",
            "mix_master",
        ],
        "stage_results": stage_results,
        "outputs": {
            "final_audio_path": mix_master["artifacts"]["final_audio_path"],
            "final_video_path": mix_master["artifacts"]["final_video_path"],
        },
    }
