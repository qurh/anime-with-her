from typing import Protocol

from worker.config import load_worker_config


class ProviderError(RuntimeError):
    """Raised when TTS provider invocation fails."""


class TtsClient(Protocol):
    provider_name: str

    def synthesize(self, text: str, duration_ms: int, style_hint: str) -> str:
        ...


class _TemplateTtsClient:
    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def synthesize(self, text: str, duration_ms: int, style_hint: str) -> str:
        _ = duration_ms
        return f"{self.provider_name}:{style_hint}:{text}"


class TtsProviderRouter:
    def __init__(self, primary_client: TtsClient, fallback_client: TtsClient):
        self.primary_client = primary_client
        self.fallback_client = fallback_client

    def synthesize(self, text: str, duration_ms: int, style_hint: str) -> dict[str, str]:
        try:
            audio_payload = self.primary_client.synthesize(
                text=text,
                duration_ms=duration_ms,
                style_hint=style_hint,
            )
            return {"provider": self.primary_client.provider_name, "audio_payload": audio_payload}
        except Exception as primary_error:
            try:
                audio_payload = self.fallback_client.synthesize(
                    text=text,
                    duration_ms=duration_ms,
                    style_hint=style_hint,
                )
                return {"provider": self.fallback_client.provider_name, "audio_payload": audio_payload}
            except Exception as fallback_error:
                raise ProviderError(
                    f"all tts providers failed: primary={primary_error}; fallback={fallback_error}"
                ) from fallback_error


def build_default_tts_router() -> TtsProviderRouter:
    config = load_worker_config()
    _ = config.should_use_real("tts_synthesis")
    return TtsProviderRouter(
        primary_client=_TemplateTtsClient(provider_name="aliyun_tts"),
        fallback_client=_TemplateTtsClient(provider_name="doubao_tts"),
    )
