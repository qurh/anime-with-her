import json
from pathlib import Path

from worker.adapters.asr_align import run_asr_align
from worker.adapters.audio_separation import run_audio_separation
from worker.adapters.media_ingest import run_media_ingest
from worker.adapters.mix_master import run_mix_master
from worker.adapters.qa_review import run_qa_review
from worker.adapters.speaker_role import run_speaker_role
from worker.adapters.tts_synthesis import run_tts_synthesis
from worker.pipelines.dub_script import rewrite_for_dubbing

STAGES = [
    "media_ingest",
    "audio_separation",
    "asr_align",
    "speaker_role",
    "dub_script",
    "tts_synthesis",
    "mix_master",
]


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
            character_style={"base_tone": "neutral"},
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


def _is_skipped(stage_name: str, start_stage: str | None) -> bool:
    if start_stage is None:
        return False
    return STAGES.index(stage_name) < STAGES.index(start_stage)


def _require_file(path: Path, stage_name: str):
    if not path.exists():
        raise RuntimeError(f"missing artifact for resume at {stage_name}: {path.as_posix()}")


def _load_skipped_media_ingest(episode_id: str, source_video: str, root: str) -> dict[str, object]:
    suffix = Path(source_video).suffix or ".mp4"
    input_dir = Path(root) / episode_id / "input"
    source_video_path = input_dir / f"source{suffix}"
    normalized_vocals_path = input_dir / "vocals_norm.wav"
    _require_file(source_video_path, "media_ingest")
    _require_file(normalized_vocals_path, "media_ingest")
    return {
        "stage_name": "media_ingest",
        "state": "skipped",
        "artifacts": {
            "source_video_path": source_video_path.as_posix(),
            "normalized_vocals_path": normalized_vocals_path.as_posix(),
        },
    }


def _load_skipped_audio_separation(episode_id: str, root: str) -> dict[str, object]:
    base = Path(root) / episode_id / "analysis" / "separation"
    vocals_path = base / "vocals.wav"
    background_path = base / "background.wav"
    effects_path = base / "effects.wav"
    _require_file(vocals_path, "audio_separation")
    _require_file(background_path, "audio_separation")
    _require_file(effects_path, "audio_separation")
    return {
        "stage_name": "audio_separation",
        "state": "skipped",
        "artifacts": {
            "vocals_path": vocals_path.as_posix(),
            "background_path": background_path.as_posix(),
            "effects_path": effects_path.as_posix(),
        },
    }


def _load_skipped_asr_align(episode_id: str, root: str) -> dict[str, object]:
    segments_path = Path(root) / episode_id / "analysis" / "asr_align" / "segments.json"
    _require_file(segments_path, "asr_align")
    segments = json.loads(segments_path.read_text(encoding="utf-8"))
    return {
        "stage_name": "asr_align",
        "state": "skipped",
        "artifacts": {
            "segments_path": segments_path.as_posix(),
            "segments": segments,
        },
    }


def _load_skipped_speaker_role(episode_id: str, root: str) -> dict[str, object]:
    base = Path(root) / episode_id / "analysis" / "speaker_role"
    speaker_segments_path = base / "speaker_segments.json"
    speakers_path = base / "speakers.json"
    _require_file(speaker_segments_path, "speaker_role")
    _require_file(speakers_path, "speaker_role")
    speaker_segments = json.loads(speaker_segments_path.read_text(encoding="utf-8"))
    speakers = json.loads(speakers_path.read_text(encoding="utf-8"))
    return {
        "stage_name": "speaker_role",
        "state": "skipped",
        "artifacts": {
            "speaker_segments_path": speaker_segments_path.as_posix(),
            "speakers_path": speakers_path.as_posix(),
            "speaker_segments": speaker_segments,
            "speakers": speakers,
        },
    }


def run_episode_pipeline(
    episode_id: str,
    source_video: str,
    root: str = "data/episodes",
    start_stage: str | None = None,
) -> dict[str, object]:
    if start_stage is not None and start_stage not in STAGES:
        raise ValueError(f"unknown start_stage: {start_stage}")

    stage_results: dict[str, dict[str, object]] = {}
    current_stage: str | None = None
    try:
        current_stage = "media_ingest"
        if _is_skipped(current_stage, start_stage):
            media_ingest = _load_skipped_media_ingest(episode_id=episode_id, source_video=source_video, root=root)
        else:
            media_ingest = run_media_ingest(episode_id=episode_id, source_video=source_video, root=root)
        stage_results[current_stage] = media_ingest

        current_stage = "audio_separation"
        if _is_skipped(current_stage, start_stage):
            audio_separation = _load_skipped_audio_separation(episode_id=episode_id, root=root)
        else:
            audio_separation = run_audio_separation(
                episode_id=episode_id,
                normalized_vocals_path=str(media_ingest["artifacts"]["normalized_vocals_path"]),
                root=root,
            )
        stage_results[current_stage] = audio_separation

        current_stage = "asr_align"
        if _is_skipped(current_stage, start_stage):
            asr_align = _load_skipped_asr_align(episode_id=episode_id, root=root)
        else:
            asr_align = run_asr_align(
                episode_id=episode_id,
                vocals_path=str(audio_separation["artifacts"]["vocals_path"]),
                root=root,
            )
        stage_results[current_stage] = asr_align

        current_stage = "speaker_role"
        if _is_skipped(current_stage, start_stage):
            speaker_role = _load_skipped_speaker_role(episode_id=episode_id, root=root)
        else:
            speaker_role = run_speaker_role(
                episode_id=episode_id,
                segments_path=str(asr_align["artifacts"]["segments_path"]),
                root=root,
            )
        stage_results[current_stage] = speaker_role

        current_stage = "dub_script"
        dub_segments = _build_dub_segments(asr_segments=list(asr_align["artifacts"]["segments"]))
        dub_script = {
            "stage_name": "dub_script",
            "state": "success",
            "segments": dub_segments,
        }
        stage_results[current_stage] = dub_script

        current_stage = "tts_synthesis"
        tts_synthesis = run_tts_synthesis(
            episode_id=episode_id,
            dub_segments=dub_segments,
            root=root,
        )
        stage_results[current_stage] = tts_synthesis

        current_stage = "mix_master"
        mix_master = run_mix_master(
            episode_id=episode_id,
            vocals_path=str(audio_separation["artifacts"]["vocals_path"]),
            background_path=str(audio_separation["artifacts"]["background_path"]),
            effects_path=str(audio_separation["artifacts"]["effects_path"]),
            tts_manifest_path=str(tts_synthesis["artifacts"]["manifest_path"]),
            root=root,
        )
        stage_results[current_stage] = mix_master

        qa_review = run_qa_review(
            episode_id=episode_id,
            final_audio_path=str(mix_master["artifacts"]["final_audio_path"]),
            final_video_path=str(mix_master["artifacts"]["final_video_path"]),
        )
        stage_results["qa_review"] = qa_review
        qa_summary = dict(qa_review["artifacts"].get("qa_summary", {}))

        return {
            "episode_id": episode_id,
            "state": "success",
            "stages": STAGES,
            "stage_results": stage_results,
            "qa_summary": qa_summary,
            "outputs": {
                "final_audio_path": mix_master["artifacts"]["final_audio_path"],
                "final_video_path": mix_master["artifacts"]["final_video_path"],
            },
        }
    except Exception as error:
        if current_stage is not None and current_stage not in stage_results:
            stage_results[current_stage] = {
                "stage_name": current_stage,
                "state": "failed",
                "error": str(error),
            }
        return {
            "episode_id": episode_id,
            "state": "failed",
            "failed_stage": current_stage,
            "error": str(error),
            "stages": STAGES,
            "stage_results": stage_results,
            "qa_summary": {},
            "outputs": {
                "final_audio_path": "",
                "final_video_path": "",
            },
        }
