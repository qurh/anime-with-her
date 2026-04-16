from worker.manifest import build_stage_manifest
from worker.storage import build_episode_layout


def test_manifest_records_review_state():
    manifest = build_stage_manifest(
        episode_id="episode_1",
        stage_name="character_analysis",
        state="needs_review",
        input_refs=["source.mp4"],
        output_refs=["character_candidates.json"],
    )
    assert manifest["state"] == "needs_review"
    assert manifest["stage_name"] == "character_analysis"


def test_episode_layout_contains_required_directories():
    layout = build_episode_layout("episode_1")
    assert layout["analysis"].endswith("data/episodes/episode_1/analysis")
    assert layout["generation"].endswith("data/episodes/episode_1/generation")
    assert layout["review"].endswith("data/episodes/episode_1/review")
