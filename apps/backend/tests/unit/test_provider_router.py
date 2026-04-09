from app.providers.contracts import ProviderError
from app.providers.router import ProviderRouter


def test_router_uses_primary_provider_when_it_succeeds():
    router = ProviderRouter()

    result = router.translate("hello")

    assert result.provider == "qwen"
    assert result.text == "hello"


def test_router_falls_back_to_secondary_when_primary_fails():
    router = ProviderRouter()

    def fail_primary(_text: str):
        raise ProviderError("qwen unavailable")

    router.primary.translate = fail_primary

    result = router.translate("hello")

    assert result.provider == "doubao"
    assert result.text == "hello"


def test_router_raises_when_both_providers_fail():
    class FailingProvider:
        def translate(self, text: str):
            raise ProviderError(f"failed: {text}")

    router = ProviderRouter(primary=FailingProvider(), secondary=FailingProvider())

    try:
        router.translate("hello")
    except ProviderError as exc:
        assert str(exc) == "failed: hello"
    else:
        raise AssertionError("ProviderError was not raised")