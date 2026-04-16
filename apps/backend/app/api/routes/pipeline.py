from __future__ import annotations

import importlib
import sys
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class RunEpisodePipelineRequest(BaseModel):
    source_video: str
    root: str = "data/episodes"


def _load_episode_runner():
    worker_app_dir = Path(__file__).resolve().parents[4] / "worker"
    worker_app_dir_str = str(worker_app_dir)
    if worker_app_dir_str not in sys.path:
        sys.path.insert(0, worker_app_dir_str)

    module = importlib.import_module("worker.pipelines.episode_pipeline_runner")
    return getattr(module, "run_episode_pipeline")


@router.post("/episodes/{episode_id}/pipeline/run", status_code=202)
def run_episode_pipeline_endpoint(episode_id: str, payload: RunEpisodePipelineRequest):
    run_episode_pipeline = _load_episode_runner()
    result = run_episode_pipeline(
        episode_id=episode_id,
        source_video=payload.source_video,
        root=payload.root,
    )
    stage_states = {
        stage_name: str(stage_result.get("state", "unknown"))
        for stage_name, stage_result in result["stage_results"].items()
    }
    return {
        "success": True,
        "data": {
            "episode_id": result["episode_id"],
            "state": result["state"],
            "stages": result["stages"],
            "stage_states": stage_states,
            "final_audio_path": result["outputs"]["final_audio_path"],
            "final_video_path": result["outputs"]["final_video_path"],
        },
    }
