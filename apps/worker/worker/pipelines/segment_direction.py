def build_segment_direction(segment_id: str, emotion: str, intensity: float, duration_target_ms: int):
    return {
        "segment_id": segment_id,
        "emotion": emotion,
        "intensity": intensity,
        "duration_target_ms": duration_target_ms,
        "speech_rate": "auto",
        "pause_style": "source_guided",
    }
