from app.domain.pipeline_run import PipelineRunState
from app.repositories.pipeline_run_store import PipelineRunStore


def test_pipeline_run_store_supports_pending_running_success_flow():
    store = PipelineRunStore()
    run = store.create_run(
        episode_id="episode_1",
        source_video="data/input/demo.mkv",
        root="data/episodes",
    )
    assert run.run_id.startswith("run_")
    assert run.state == PipelineRunState.PENDING

    store.update_run_state(run.run_id, PipelineRunState.RUNNING)
    store.set_stage_state(run.run_id, "media_ingest", "success")
    store.update_run_state(
        run.run_id,
        PipelineRunState.SUCCESS,
        outputs={
            "final_audio_path": "data/episodes/episode_1/output/final_audio_mix.wav",
            "final_video_path": "data/episodes/episode_1/output/final_dubbed.mp4",
        },
    )

    updated = store.get_run(run.run_id)
    assert updated is not None
    assert updated.state == PipelineRunState.SUCCESS
    assert updated.stage_states["media_ingest"] == "success"
    assert updated.outputs["final_video_path"].endswith("final_dubbed.mp4")


def test_pipeline_run_store_supports_failed_flow_and_recent_query():
    store = PipelineRunStore()
    run_1 = store.create_run(
        episode_id="episode_1",
        source_video="data/input/a.mkv",
        root="data/episodes",
    )
    run_2 = store.create_run(
        episode_id="episode_1",
        source_video="data/input/b.mkv",
        root="data/episodes",
    )
    _ = store.create_run(
        episode_id="episode_2",
        source_video="data/input/c.mkv",
        root="data/episodes",
    )

    store.update_run_state(run_2.run_id, PipelineRunState.RUNNING)
    store.update_run_state(
        run_2.run_id,
        PipelineRunState.FAILED,
        failed_stage="tts_synthesis",
        error_message="provider timeout",
    )

    failed = store.get_run(run_2.run_id)
    assert failed is not None
    assert failed.state == PipelineRunState.FAILED
    assert failed.failed_stage == "tts_synthesis"
    assert failed.error_message == "provider timeout"

    recent = store.list_runs_by_episode("episode_1")
    assert [item.run_id for item in recent] == [run_2.run_id, run_1.run_id]
