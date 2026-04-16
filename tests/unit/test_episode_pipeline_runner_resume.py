from pathlib import Path

import worker.pipelines.episode_pipeline_runner as runner_module


def test_episode_pipeline_runner_can_resume_from_asr_align(tmp_path, monkeypatch):
    root = str(tmp_path / "episodes")
    episode_id = "episode_resume_1"
    source_video = "data/input/demo.mkv"

    first_run = runner_module.run_episode_pipeline(
        episode_id=episode_id,
        source_video=source_video,
        root=root,
    )
    assert first_run["state"] == "success"

    def _raise_if_called(*args, **kwargs):
        raise RuntimeError("media ingest should be skipped when resuming from asr_align")

    monkeypatch.setattr(runner_module, "run_media_ingest", _raise_if_called)

    resumed = runner_module.run_episode_pipeline(
        episode_id=episode_id,
        source_video=source_video,
        root=root,
        start_stage="asr_align",
    )

    assert resumed["state"] == "success"
    assert resumed["stage_results"]["media_ingest"]["state"] == "skipped"
    assert resumed["stage_results"]["audio_separation"]["state"] == "skipped"
    assert resumed["stage_results"]["asr_align"]["state"] == "success"
    assert Path(resumed["outputs"]["final_audio_path"]).exists()
    assert Path(resumed["outputs"]["final_video_path"]).exists()
