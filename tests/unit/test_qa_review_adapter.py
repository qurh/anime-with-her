from worker.adapters.qa_review import run_qa_review


def test_qa_review_returns_summary_scores():
    result = run_qa_review(
        episode_id="episode_qa_1",
        final_audio_path="data/episodes/episode_qa_1/output/final_audio_mix.wav",
        final_video_path="data/episodes/episode_qa_1/output/final_dubbed.mp4",
    )

    assert result["stage_name"] == "qa_review"
    assert result["state"] == "success"
    summary = result["artifacts"]["qa_summary"]
    assert 0.0 <= summary["timing_fit_score"] <= 1.0
    assert 0.0 <= summary["voice_stability_score"] <= 1.0
    assert 0.0 <= summary["mix_balance_score"] <= 1.0
    assert "threshold_flags" in summary
    assert isinstance(summary["threshold_flags"], dict)
