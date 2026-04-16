import worker.pipelines.episode_pipeline_runner as runner_module


def test_episode_pipeline_runner_reports_failed_stage_and_preserves_successful_outputs(tmp_path, monkeypatch):
    def _raise_audio_separation_failure(*args, **kwargs):
        raise RuntimeError("audio separation crashed")

    monkeypatch.setattr(
        runner_module,
        "run_audio_separation",
        _raise_audio_separation_failure,
    )

    result = runner_module.run_episode_pipeline(
        episode_id="episode_fail_1",
        source_video="data/input/demo.mkv",
        root=str(tmp_path / "episodes"),
    )

    assert result["state"] == "failed"
    assert result["failed_stage"] == "audio_separation"
    assert "audio separation crashed" in result["error"]
    assert result["stage_results"]["media_ingest"]["state"] == "success"
    assert result["stage_results"]["audio_separation"]["state"] == "failed"
