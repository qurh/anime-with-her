import pytest

from worker.adapters.tts_provider import ProviderError, TtsProviderRouter


class _FakeTtsClient:
    def __init__(self, provider_name: str, should_fail: bool = False):
        self.provider_name = provider_name
        self.should_fail = should_fail
        self.calls = 0

    def synthesize(self, text: str, duration_ms: int, style_hint: str) -> str:
        self.calls += 1
        if self.should_fail:
            raise ProviderError(f"{self.provider_name} failed")
        return f"{self.provider_name}|{duration_ms}|{style_hint}|{text}"


def test_tts_router_uses_primary_provider_when_available():
    primary = _FakeTtsClient(provider_name="aliyun_tts")
    fallback = _FakeTtsClient(provider_name="doubao_tts")
    router = TtsProviderRouter(primary_client=primary, fallback_client=fallback)

    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert result["provider"] == "aliyun_tts"
    assert "aliyun_tts" in result["audio_payload"]
    assert primary.calls == 1
    assert fallback.calls == 0


def test_tts_router_falls_back_when_primary_fails():
    primary = _FakeTtsClient(provider_name="aliyun_tts", should_fail=True)
    fallback = _FakeTtsClient(provider_name="doubao_tts")
    router = TtsProviderRouter(primary_client=primary, fallback_client=fallback)

    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert result["provider"] == "doubao_tts"
    assert "doubao_tts" in result["audio_payload"]
    assert primary.calls == 1
    assert fallback.calls == 1


def test_tts_router_raises_when_all_providers_fail():
    primary = _FakeTtsClient(provider_name="aliyun_tts", should_fail=True)
    fallback = _FakeTtsClient(provider_name="doubao_tts", should_fail=True)
    router = TtsProviderRouter(primary_client=primary, fallback_client=fallback)

    with pytest.raises(ProviderError):
        router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")
