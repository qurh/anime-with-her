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


def test_qa_review_metrics_are_deterministic_for_same_artifacts(tmp_path):
    audio_path = tmp_path / "final_audio_mix.wav"
    video_path = tmp_path / "final_dubbed.mp4"
    audio_path.write_bytes(b"audio-bytes")
    video_path.write_bytes(b"video-bytes")

    summary_one = run_qa_review(
        episode_id="episode_qa_deterministic",
        final_audio_path=str(audio_path),
        final_video_path=str(video_path),
    )["artifacts"]["qa_summary"]
    summary_two = run_qa_review(
        episode_id="episode_qa_deterministic",
        final_audio_path=str(audio_path),
        final_video_path=str(video_path),
    )["artifacts"]["qa_summary"]

    assert summary_one == summary_two


def test_qa_review_metrics_change_when_artifact_inputs_change(tmp_path):
    audio_path = tmp_path / "final_audio_mix.wav"
    video_path = tmp_path / "final_dubbed.mp4"
    audio_path.write_bytes(b"a" * 10)
    video_path.write_bytes(b"v" * 10)

    summary_before = run_qa_review(
        episode_id="episode_qa_sensitive",
        final_audio_path=str(audio_path),
        final_video_path=str(video_path),
    )["artifacts"]["qa_summary"]

    audio_path.write_bytes(b"a" * 17)

    summary_after = run_qa_review(
        episode_id="episode_qa_sensitive",
        final_audio_path=str(audio_path),
        final_video_path=str(video_path),
    )["artifacts"]["qa_summary"]

    assert any(
        summary_before[metric_name] != summary_after[metric_name]
        for metric_name in ("timing_fit_score", "voice_stability_score", "mix_balance_score")
    )
