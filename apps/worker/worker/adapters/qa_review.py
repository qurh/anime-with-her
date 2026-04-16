from worker.manifest import build_stage_manifest


def run_qa_review(episode_id: str, final_audio_path: str, final_video_path: str) -> dict[str, object]:
    qa_summary = {
        "timing_fit_score": 0.86,
        "voice_stability_score": 0.9,
        "mix_balance_score": 0.88,
    }
    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="qa_review",
        state="success",
        input_refs=[final_audio_path, final_video_path],
        output_refs=[],
    )
    return {
        **manifest,
        "artifacts": {
            "qa_summary": qa_summary,
        },
    }
