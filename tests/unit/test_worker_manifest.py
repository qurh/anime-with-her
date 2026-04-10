def test_manifest_contains_stage_and_artifact_paths():
    from apps.worker.worker.manifest import build_stage_manifest

    manifest = build_stage_manifest(
        "job_1",
        "asr",
        ["data/intermediate/job_1/asr.json"],
    )

    assert manifest["job_id"] == "job_1"
    assert manifest["stage"] == "asr"
    assert manifest["artifacts"] == ["data/intermediate/job_1/asr.json"]
