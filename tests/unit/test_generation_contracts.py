from worker.pipelines.dub_script import rewrite_for_dubbing
from worker.pipelines.segment_direction import build_segment_direction


def test_rewrite_for_dubbing_respects_character_style():
    result = rewrite_for_dubbing(
        source_text="ありがとう",
        literal_translation="谢谢",
        character_style={"base_tone": "温柔但坚定", "speech_rate": "中速"},
        duration_ms=1200,
    )
    assert result["dub_text"]
    assert result["style_hint"] == "温柔但坚定"


def test_segment_direction_contains_performance_controls():
    direction = build_segment_direction(segment_id="seg_1", emotion="紧张", intensity=0.7, duration_target_ms=1500)
    assert direction["emotion"] == "紧张"
    assert direction["duration_target_ms"] == 1500
