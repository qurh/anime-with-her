from collections.abc import Sequence


def build_stage_manifest(job_id: str, stage: str, artifacts: Sequence[str]) -> dict[str, object]:
    return {
        "job_id": job_id,
        "stage": stage,
        "artifacts": list(artifacts),
    }
