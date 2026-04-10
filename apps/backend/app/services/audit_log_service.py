TTL_DAYS = 30


def should_delete(record_age_days: int) -> bool:
    return record_age_days > TTL_DAYS
