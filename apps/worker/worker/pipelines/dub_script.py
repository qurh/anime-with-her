def rewrite_for_dubbing(
    source_text: str,
    literal_translation: str,
    character_style: dict[str, object],
    duration_ms: int,
):
    return {
        "source_text": source_text,
        "literal_translation": literal_translation,
        "dub_text": literal_translation,
        "duration_target_ms": duration_ms,
        "style_hint": str(character_style.get("base_tone", "")),
    }
