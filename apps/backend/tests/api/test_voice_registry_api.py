def test_create_voice_profile_version(client):
    payload = {
        "series": "Naruto",
        "character": "Kakashi",
        "sample_path": "data/intermediate/job_1/kakashi.wav",
    }
    resp = client.post("/api/v1/voice-registry/versions", json=payload)

    assert resp.status_code == 201
    assert resp.json()["data"]["status"] == "auto_collected"
