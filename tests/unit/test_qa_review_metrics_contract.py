import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "worker"))

from worker.adapters.qa_review import run_qa_review


def test_qa_review_threshold_flags_exist_and_are_explainable():
    result = run_qa_review(
        episode_id="episode_contract_1",
        final_audio_path="data/episodes/episode_contract_1/output/final_audio_mix.wav",
        final_video_path="data/episodes/episode_contract_1/output/final_dubbed.mp4",
    )

    summary = result["artifacts"]["qa_summary"]
    assert "threshold_flags" in summary

    flags = summary["threshold_flags"]
    assert isinstance(flags, dict)
    assert flags

    for metric_name, detail in flags.items():
        assert isinstance(metric_name, str)
        assert isinstance(detail, dict)
        assert isinstance(detail.get("is_below_threshold"), bool)
        assert isinstance(detail.get("reason"), str)
        assert detail["reason"].strip()
