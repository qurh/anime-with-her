def test_start_generation_after_character_approval(client):
    response = client.post("/api/v1/episodes/episode_1/generation", json={"approved": True})
    assert response.status_code == 202
    assert response.json()["data"]["stage_name"] == "episode_generation"


def test_regenerate_segment_accepts_director_overrides(client):
    response = client.post(
        "/api/v1/episodes/episode_1/segments/seg_1/regenerate",
        json={
            "dub_text": "我不会再逃了。",
            "emotion": "坚定",
            "reference_sample_id": "sample_1",
        },
    )
    assert response.status_code == 202
    assert response.json()["data"]["segment_id"] == "seg_1"
