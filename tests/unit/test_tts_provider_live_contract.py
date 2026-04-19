import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "apps" / "worker"))

from worker.adapters import tts_provider as tts_provider_module


def test_tts_live_contract_defaults_to_fake_when_no_credentials(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("ALIYUN_TTS_API_KEY", raising=False)
    monkeypatch.delenv("DOUBAO_TTS_API_KEY", raising=False)

    router = tts_provider_module.build_default_tts_router()
    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert result["provider"] == "aliyun_tts"
    assert result["audio_payload"].startswith("aliyun_tts:")


def test_tts_live_contract_uses_live_primary_when_credentials_present(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.setenv("ALIYUN_TTS_API_KEY", "aliyun-key")
    monkeypatch.delenv("DOUBAO_TTS_API_KEY", raising=False)

    monkeypatch.setattr(
        tts_provider_module,
        "_invoke_live_tts",
        lambda provider_name, api_key, text, duration_ms, style_hint, timeout_ms: "live-primary-audio",
    )

    router = tts_provider_module.build_default_tts_router()
    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    assert result["provider"] == "aliyun_tts"
    assert result["audio_payload"] == "live-primary-audio"


def test_tts_live_contract_falls_back_when_primary_live_fails(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.setenv("ALIYUN_TTS_API_KEY", "aliyun-key")
    monkeypatch.delenv("DOUBAO_TTS_API_KEY", raising=False)

    def _fake_invoke(provider_name, api_key, text, duration_ms, style_hint, timeout_ms):
        _ = (api_key, text, duration_ms, style_hint, timeout_ms)
        if provider_name == "aliyun_tts":
            raise RuntimeError("primary timeout")
        return "live-fallback-audio"

    monkeypatch.setattr(tts_provider_module, "_invoke_live_tts", _fake_invoke)

    router = tts_provider_module.build_default_tts_router()
    result = router.synthesize(text="你好", duration_ms=1000, style_hint="温柔")

    # fallback may be live (if configured) or fake; at least it must not be primary
    assert result["provider"] != "aliyun_tts"
    assert result["audio_payload"]
