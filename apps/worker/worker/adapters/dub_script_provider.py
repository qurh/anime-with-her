from typing import Protocol


class ProviderError(RuntimeError):
    """Raised when provider invocation fails."""


class DubScriptClient(Protocol):
    provider_name: str

    def rewrite(
        self,
        source_text: str,
        literal_translation: str,
        character_style: dict[str, object],
        duration_ms: int,
    ) -> str:
        ...


class _TemplateClient:
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def rewrite(
        self,
        source_text: str,
        literal_translation: str,
        character_style: dict[str, object],
        duration_ms: int,
    ) -> str:
        tone = str(character_style.get("base_tone", "")).strip()
        _ = source_text
        _ = duration_ms
        return f"{literal_translation}".strip() or tone or "..."


class DubScriptProviderRouter:
    def __init__(self, primary_client: DubScriptClient, fallback_client: DubScriptClient):
        self.primary_client = primary_client
        self.fallback_client = fallback_client

    def rewrite_for_dubbing(
        self,
        source_text: str,
        literal_translation: str,
        character_style: dict[str, object],
        duration_ms: int,
    ) -> dict[str, str]:
        try:
            dub_text = self.primary_client.rewrite(
                source_text=source_text,
                literal_translation=literal_translation,
                character_style=character_style,
                duration_ms=duration_ms,
            )
            return {"provider": self.primary_client.provider_name, "dub_text": dub_text}
        except Exception as primary_error:
            try:
                dub_text = self.fallback_client.rewrite(
                    source_text=source_text,
                    literal_translation=literal_translation,
                    character_style=character_style,
                    duration_ms=duration_ms,
                )
                return {"provider": self.fallback_client.provider_name, "dub_text": dub_text}
            except Exception as fallback_error:
                raise ProviderError(
                    f"all dub script providers failed: primary={primary_error}; fallback={fallback_error}"
                ) from fallback_error


def build_default_dub_script_router() -> DubScriptProviderRouter:
    return DubScriptProviderRouter(
        primary_client=_TemplateClient(provider_name="qwen"),
        fallback_client=_TemplateClient(provider_name="doubao"),
    )
