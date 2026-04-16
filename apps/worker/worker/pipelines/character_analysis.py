from worker.manifest import build_stage_manifest


def run_character_analysis(episode_id: str, source_video: str) -> dict[str, object]:
    review_payload = {
        "characters": [
            {
                "candidate_id": "candidate_1",
                "display_name": "角色候选1",
                "confidence": 0.82,
            }
        ],
        "style_cards": [
            {
                "candidate_id": "candidate_1",
                "base_tone": "冷静但情绪压抑",
                "speech_rate": "中速",
            }
        ],
    }
    manifest = build_stage_manifest(
        episode_id=episode_id,
        stage_name="character_analysis",
        state="needs_review",
        input_refs=[source_video],
        output_refs=[f"data/episodes/{episode_id}/analysis/character_candidates.json"],
    )
    return {**manifest, "review_payload": review_payload}
