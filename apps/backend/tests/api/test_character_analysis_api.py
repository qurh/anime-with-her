def test_start_character_analysis_moves_episode_to_review(client):
    response = client.post(
        "/api/v1/episodes/episode_1/analysis/character",
        json={"source_video": "data/episodes/episode_1/input/source.mp4"},
    )
    assert response.status_code == 202
    assert response.json()["data"]["state"] == "needs_review"


def test_approve_character_analysis_returns_approved_state(client):
    response = client.post(
        "/api/v1/episodes/episode_1/analysis/character/approve",
        json={
            "approved_characters": [
                {
                    "candidate_id": "candidate_1",
                    "display_name": "女主角",
                    "base_tone": "温柔但坚定",
                }
            ]
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["state"] == "approved"
