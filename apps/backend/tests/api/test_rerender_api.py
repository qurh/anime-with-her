def test_rerender_starts_new_job_after_voice_update(client):
    resp = client.post("/api/v1/rerender", json={"source_job_id": "job_1", "voice_version_id": "v2"})

    assert resp.status_code == 202
    assert resp.json()["data"]["state"] == "rerendering"
