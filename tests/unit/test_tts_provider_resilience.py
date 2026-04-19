import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "apps" / "worker"))

from worker.adapters import tts_provider as tts_provider_module


def test_tts_resilience_retries_timeout_and_recovers(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.setenv("ALIYUN_TTS_API_KEY", "aliyun-key")
    monkeypatch.delenv("DOUBAO_TTS_API_KEY", raising=False)
    monkeypatch.setenv("TTS_MAX_RETRIES", "1")
    monkeypatch.setenv("TTS_TIMEOUT_MS", "150")

    attempts = {"aliyun_tts": 0}

    timeout_values: list[int] = []

    def _fake_invoke(provider_name, api_key, text, duration_ms, style_hint, timeout_ms):
        _ = (api_key, text, duration_ms, style_hint)
        timeout_values.append(timeout_ms)
        if provider_name == "aliyun_tts":
            attempts["aliyun_tts"] += 1
            if attempts["aliyun_tts"] == 1:
                raise TimeoutError("primary timeout")
            return "recovered-primary-audio"
        return "unexpected-fallback-audio"

    monkeypatch.setattr(tts_provider_module, "_invoke_live_tts", _fake_invoke)

    router = tts_provider_module.build_default_tts_router()
    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert attempts["aliyun_tts"] == 2
    assert timeout_values == [150, 150]
    assert result["provider"] == "aliyun_tts"
    assert result["audio_payload"] == "recovered-primary-audio"


def test_tts_resilience_exhausts_retries_before_fallback(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.setenv("ALIYUN_TTS_API_KEY", "aliyun-key")
    monkeypatch.delenv("DOUBAO_TTS_API_KEY", raising=False)
    monkeypatch.setenv("TTS_MAX_RETRIES", "2")
    monkeypatch.setenv("TTS_TIMEOUT_MS", "150")

    attempts = {"aliyun_tts": 0}

    def _fake_invoke(provider_name, api_key, text, duration_ms, style_hint, timeout_ms):
        _ = (api_key, text, duration_ms, style_hint, timeout_ms)
        if provider_name == "aliyun_tts":
            attempts["aliyun_tts"] += 1
            raise TimeoutError("primary timeout")
        return "unexpected-fallback-audio"

    monkeypatch.setattr(tts_provider_module, "_invoke_live_tts", _fake_invoke)

    router = tts_provider_module.build_default_tts_router()
    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert attempts["aliyun_tts"] == 3
    assert result["provider"] == "doubao_tts"
    assert result["audio_payload"].startswith("doubao_tts:")


def test_tts_resilience_passes_timeout_env_to_live_invocation(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.setenv("ALIYUN_TTS_API_KEY", "aliyun-key")
    monkeypatch.delenv("DOUBAO_TTS_API_KEY", raising=False)
    monkeypatch.setenv("TTS_TIMEOUT_MS", "222")

    captured_timeout_values: list[int] = []

    def _fake_invoke(provider_name, api_key, text, duration_ms, style_hint, timeout_ms):
        _ = (provider_name, api_key, text, duration_ms, style_hint)
        captured_timeout_values.append(timeout_ms)
        return "live-primary-audio"

    monkeypatch.setattr(tts_provider_module, "_invoke_live_tts", _fake_invoke)

    router = tts_provider_module.build_default_tts_router()
    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert captured_timeout_values == [222]
    assert result["provider"] == "aliyun_tts"
    assert result["audio_payload"] == "live-primary-audio"


def test_tts_resilience_retries_timeout_like_non_builtin_timeout_error(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.setenv("ALIYUN_TTS_API_KEY", "aliyun-key")
    monkeypatch.delenv("DOUBAO_TTS_API_KEY", raising=False)
    monkeypatch.setenv("TTS_MAX_RETRIES", "1")

    attempts = {"aliyun_tts": 0}

    class ProviderRequestTimeout(Exception):
        pass

    def _fake_invoke(provider_name, api_key, text, duration_ms, style_hint, timeout_ms):
        _ = (api_key, text, duration_ms, style_hint, timeout_ms)
        if provider_name == "aliyun_tts":
            attempts["aliyun_tts"] += 1
            if attempts["aliyun_tts"] == 1:
                raise ProviderRequestTimeout("provider timed out")
            return "recovered-after-timeout-like-error"
        return "unexpected-fallback-audio"

    monkeypatch.setattr(tts_provider_module, "_invoke_live_tts", _fake_invoke)

    router = tts_provider_module.build_default_tts_router()
    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert attempts["aliyun_tts"] == 2
    assert result["provider"] == "aliyun_tts"
    assert result["audio_payload"] == "recovered-after-timeout-like-error"
