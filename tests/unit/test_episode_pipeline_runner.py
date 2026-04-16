from pathlib import Path

from worker.pipelines.episode_pipeline_runner import run_episode_pipeline


def test_episode_pipeline_runner_executes_all_core_stages(tmp_path: Path):
    result = run_episode_pipeline(
        episode_id="episode_1",
        source_video="data/input/demo.mkv",
        root=str(tmp_path / "episodes"),
    )

    assert result["episode_id"] == "episode_1"
    assert result["state"] == "success"
    assert result["stages"] == [
        "media_ingest",
        "audio_separation",
        "asr_align",
        "speaker_role",
        "dub_script",
        "tts_synthesis",
        "mix_master",
    ]

    stage_results = result["stage_results"]
    assert stage_results["dub_script"]["segments"][0]["provider"] in {"qwen", "doubao"}
    assert stage_results["tts_synthesis"]["artifacts"]["segments"][0]["provider"] in {"aliyun_tts", "doubao_tts"}
    assert stage_results["mix_master"]["state"] == "success"
    assert 0.0 <= result["qa_summary"]["timing_fit_score"] <= 1.0
    assert 0.0 <= result["qa_summary"]["voice_stability_score"] <= 1.0
    assert 0.0 <= result["qa_summary"]["mix_balance_score"] <= 1.0

    assert Path(result["outputs"]["final_audio_path"]).exists()
    assert Path(result["outputs"]["final_video_path"]).exists()
