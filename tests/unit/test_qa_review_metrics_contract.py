import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "worker"))

from worker.adapters.qa_review import run_qa_review
from worker.pipelines import episode_pipeline_runner


def test_qa_review_threshold_flags_exist_and_are_explainable():
    result = run_qa_review(
        episode_id="episode_contract_1",
        final_audio_path="data/episodes/episode_contract_1/output/final_audio_mix.wav",
        final_video_path="data/episodes/episode_contract_1/output/final_dubbed.mp4",
    )

    summary = result["artifacts"]["qa_summary"]
    assert "threshold_flags" in summary

    required_metrics = {"timing_fit_score", "voice_stability_score", "mix_balance_score"}
    assert required_metrics.issubset(summary.keys())

    flags = summary["threshold_flags"]
    assert isinstance(flags, dict)
    assert flags
    assert set(flags.keys()) == required_metrics

    for metric_name in required_metrics:
        detail = flags[metric_name]
        assert isinstance(detail, dict)
        assert isinstance(detail.get("is_below_threshold"), bool)
        assert isinstance(detail.get("reason"), str)
        assert detail["reason"].strip()


def test_episode_pipeline_fails_when_qa_summary_contract_is_invalid(tmp_path, monkeypatch):
    def _invalid_qa_review(*args, **kwargs):
        return {
            "stage_name": "qa_review",
            "state": "success",
            "artifacts": {
                "qa_summary": {
                    "timing_fit_score": 0.9,
                }
            },
        }

    monkeypatch.setattr(episode_pipeline_runner, "run_qa_review", _invalid_qa_review)

    result = episode_pipeline_runner.run_episode_pipeline(
        episode_id="episode_contract_invalid_qa",
        source_video="data/input/demo.mkv",
        root=str(tmp_path / "episodes"),
    )

    assert result["state"] == "failed"
    assert result["failed_stage"] == "qa_review"
    assert "qa_summary" in result["error"]
