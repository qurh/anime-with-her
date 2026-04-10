def test_fast_flow_reaches_partial_or_done(client):
    create = client.post("/api/v1/jobs", json={"input_video": "data/input/demo.mp4"})
    job_id = create.json()["data"]["job_id"]

    _ = client.get(f"/api/v1/jobs/{job_id}")
    status = client.get(f"/api/v1/jobs/{job_id}")

    assert status.status_code == 200
    assert status.json()["data"]["state"] in {"running", "partial_done", "done"}
