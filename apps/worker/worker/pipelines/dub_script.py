from worker.adapters.dub_script_provider import (
    DubScriptProviderRouter,
    build_default_dub_script_router,
)


def rewrite_for_dubbing(
    source_text: str,
    literal_translation: str,
    character_style: dict[str, object],
    duration_ms: int,
    provider_router: DubScriptProviderRouter | None = None,
):
    router = provider_router or build_default_dub_script_router()
    provider_result = router.rewrite_for_dubbing(
        source_text=source_text,
        literal_translation=literal_translation,
        character_style=character_style,
        duration_ms=duration_ms,
    )
    return {
        "source_text": source_text,
        "literal_translation": literal_translation,
        "dub_text": provider_result["dub_text"],
        "duration_target_ms": duration_ms,
        "style_hint": str(character_style.get("base_tone", "")),
        "provider": provider_result["provider"],
    }
