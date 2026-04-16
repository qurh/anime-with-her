import pytest

from worker.adapters.dub_script_provider import DubScriptProviderRouter, ProviderError


class _FakeClient:
    def __init__(self, provider_name: str, should_fail: bool = False):
        self.provider_name = provider_name
        self.should_fail = should_fail
        self.calls = 0

    def rewrite(
        self,
        source_text: str,
        literal_translation: str,
        character_style: dict[str, object],
        duration_ms: int,
    ) -> str:
        self.calls += 1
        if self.should_fail:
            raise ProviderError(f"{self.provider_name} failed")
        tone = str(character_style.get("base_tone", "")).strip()
        return f"{literal_translation} [{self.provider_name}|{tone}|{duration_ms}]"


def test_router_uses_primary_provider_when_available():
    primary = _FakeClient(provider_name="qwen")
    fallback = _FakeClient(provider_name="doubao")
    router = DubScriptProviderRouter(primary_client=primary, fallback_client=fallback)

    result = router.rewrite_for_dubbing(
        source_text="thanks",
        literal_translation="谢谢",
        character_style={"base_tone": "calm"},
        duration_ms=1200,
    )

    assert result["provider"] == "qwen"
    assert "qwen" in result["dub_text"]
    assert primary.calls == 1
    assert fallback.calls == 0


def test_router_falls_back_when_primary_fails():
    primary = _FakeClient(provider_name="qwen", should_fail=True)
    fallback = _FakeClient(provider_name="doubao")
    router = DubScriptProviderRouter(primary_client=primary, fallback_client=fallback)

    result = router.rewrite_for_dubbing(
        source_text="thanks",
        literal_translation="谢谢",
        character_style={"base_tone": "calm"},
        duration_ms=1200,
    )

    assert result["provider"] == "doubao"
    assert "doubao" in result["dub_text"]
    assert primary.calls == 1
    assert fallback.calls == 1


def test_router_raises_when_all_providers_fail():
    primary = _FakeClient(provider_name="qwen", should_fail=True)
    fallback = _FakeClient(provider_name="doubao", should_fail=True)
    router = DubScriptProviderRouter(primary_client=primary, fallback_client=fallback)

    with pytest.raises(ProviderError):
        router.rewrite_for_dubbing(
            source_text="thanks",
            literal_translation="谢谢",
            character_style={"base_tone": "calm"},
            duration_ms=1200,
        )
