def start_rerender(source_job_id: str, voice_version_id: str) -> dict[str, str]:
    _ = (source_job_id, voice_version_id)
    return {"job_id": "job_r1", "state": "rerendering"}
