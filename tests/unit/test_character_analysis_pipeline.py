from worker.pipelines.character_analysis import run_character_analysis


def test_character_analysis_returns_review_payload():
    result = run_character_analysis(episode_id="episode_1", source_video="demo.mp4")
    assert result["stage_name"] == "character_analysis"
    assert result["state"] == "needs_review"
    assert result["review_payload"]["characters"][0]["display_name"] == "角色候选1"
    assert result["review_payload"]["style_cards"][0]["base_tone"]
