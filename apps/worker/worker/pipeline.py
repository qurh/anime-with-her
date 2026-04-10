from .manifest import build_stage_manifest


def run_stage(job_id: str, stage: str, artifacts: list[str]) -> dict[str, object]:
    return build_stage_manifest(job_id, stage, artifacts)


def run_pipeline(job_id: str) -> list[dict[str, object]]:
    return [run_stage(job_id, "asr", [])]
