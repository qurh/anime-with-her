from pathlib import Path

import worker.adapters.media_ingest as media_ingest_module


def test_media_ingest_real_mode_uses_ffmpeg_when_available(tmp_path: Path, monkeypatch):
    source_path = tmp_path / "input" / "demo.mkv"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text("fake source", encoding="utf-8")

    called: dict[str, str] = {}

    def _fake_ffmpeg_run(source_video: str, output_wav_path: Path):
        called["source_video"] = source_video
        called["output_wav_path"] = output_wav_path.as_posix()
        output_wav_path.write_text("real ffmpeg output", encoding="utf-8")

    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)
    monkeypatch.setattr(media_ingest_module, "_ffmpeg_available", lambda: True)
    monkeypatch.setattr(media_ingest_module, "_run_ffmpeg_extract_normalize", _fake_ffmpeg_run)

    result = media_ingest_module.run_media_ingest(
        episode_id="episode_real_1",
        source_video=source_path.as_posix(),
        root=str(tmp_path / "episodes"),
    )

    assert result["execution_mode"] == "real"
    assert result["warnings"] == []
    assert called["source_video"] == source_path.as_posix()
    assert called["output_wav_path"].endswith("/episodes/episode_real_1/input/vocals_norm.wav")
    assert Path(result["artifacts"]["normalized_vocals_path"]).read_text(encoding="utf-8") == "real ffmpeg output"


def test_media_ingest_real_mode_falls_back_to_fake_when_ffmpeg_missing(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("WORKER_MODE", "real")
    monkeypatch.delenv("WORKER_REAL_STAGES", raising=False)
    monkeypatch.setattr(media_ingest_module, "_ffmpeg_available", lambda: False)

    result = media_ingest_module.run_media_ingest(
        episode_id="episode_real_2",
        source_video="data/input/demo.mkv",
        root=str(tmp_path / "episodes"),
    )

    assert result["execution_mode"] == "fake"
    assert "ffmpeg unavailable" in result["warnings"][0]
    assert Path(result["artifacts"]["normalized_vocals_path"]).exists()
