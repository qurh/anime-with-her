def test_retention_keeps_latest_two_versions():
    from app.services.version_retention_service import retained_versions

    versions = ["v1", "v2", "v3"]
    assert retained_versions(versions) == ["v2", "v3"]
