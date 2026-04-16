import os
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


def _invoke_live_tts(
    provider_name: str,
    api_key: str,
    text: str,
    duration_ms: int,
    style_hint: str,
) -> str:
    _ = (provider_name, api_key, duration_ms, style_hint)
    # real provider call should be implemented in next iteration.
    return f"live:{text}"


class _LiveTtsClient:
    def __init__(self, provider_name: str, api_key_env: str):
        self.provider_name = provider_name
        self.api_key_env = api_key_env

    def synthesize(self, text: str, duration_ms: int, style_hint: str) -> str:
        api_key = os.getenv(self.api_key_env, "").strip()
        if not api_key:
            raise ProviderError(f"missing credential: {self.api_key_env}")
        return _invoke_live_tts(
            provider_name=self.provider_name,
            api_key=api_key,
            text=text,
            duration_ms=duration_ms,
            style_hint=style_hint,
        )


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


def _build_default_client(provider_name: str, api_key_env: str, wants_real: bool) -> TtsClient:
    if wants_real and os.getenv(api_key_env, "").strip():
        return _LiveTtsClient(provider_name=provider_name, api_key_env=api_key_env)
    return _TemplateTtsClient(provider_name=provider_name)


def build_default_tts_router() -> TtsProviderRouter:
    config = load_worker_config()
    wants_real = config.should_use_real("tts_synthesis")
    return TtsProviderRouter(
        primary_client=_build_default_client("aliyun_tts", "ALIYUN_TTS_API_KEY", wants_real),
        fallback_client=_build_default_client("doubao_tts", "DOUBAO_TTS_API_KEY", wants_real),
    )
