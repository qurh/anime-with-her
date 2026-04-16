from worker.config import load_worker_config


def test_worker_config_defaults_to_fake_mode(monkeypatch):
    monkeypatch.delenv("WORKER_MODE", raising=False)
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)

    config = load_worker_config()
    assert config.mode == "fake"
    assert config.should_use_real("media_ingest") is False
    assert config.should_use_real("tts_synthesis") is False


def test_worker_config_real_mode_enables_all_stages(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)

    config = load_worker_config()
    assert config.mode == "real"
    assert config.should_use_real("media_ingest") is True
    assert config.should_use_real("asr_align") is True
    assert config.should_use_real("tts_synthesis") is True


def test_worker_config_hybrid_mode_enables_only_selected_stages(monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "hybrid")
    monkeypatch.setenv("WORKER_REAL_STAGES", "media_ingest, tts_synthesis")

    config = load_worker_config()
    assert config.mode == "hybrid"
    assert config.should_use_real("media_ingest") is True
    assert config.should_use_real("tts_synthesis") is True
    assert config.should_use_real("asr_align") is False
