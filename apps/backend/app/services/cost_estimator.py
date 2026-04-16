from pathlib import Path


def estimate_pipeline_cost(source_video: str) -> dict[str, float | int]:
    source_path = Path(source_video)
    if source_path.exists() and source_path.is_file():
        size_gb = source_path.stat().st_size / (1024**3)
        estimated_cost_cny = max(0.2, round(size_gb * 4.0, 2))
        estimated_duration_seconds = max(30, int(size_gb * 120))
    else:
        estimated_cost_cny = 0.8
        estimated_duration_seconds = 90

    return {
        "estimated_cost_cny": estimated_cost_cny,
        "estimated_duration_seconds": estimated_duration_seconds,
    }
