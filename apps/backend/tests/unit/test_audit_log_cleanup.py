def test_cleanup_deletes_records_older_than_30_days():
    from app.services.audit_log_service import should_delete

    assert should_delete(record_age_days=31) is True
    assert should_delete(record_age_days=30) is False
