from datetime import UTC, datetime


def build_stage_manifest(
    episode_id: str,
    stage_name: str,
    state: str,
    input_refs: list[str],
    output_refs: list[str],
):
    return {
        "episode_id": episode_id,
        "stage_name": stage_name,
        "state": state,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "created_at": datetime.now(UTC).isoformat(),
    }