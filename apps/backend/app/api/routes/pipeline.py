from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.domain.pipeline_run import PipelineRun, PipelineRunState
from app.repositories.pipeline_run_store import PipelineRunStore
from app.services.cost_estimator import estimate_pipeline_cost

router = APIRouter()
pipeline_run_store = PipelineRunStore()


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


def _execute_pipeline(run_id: str, episode_id: str, source_video: str, root: str):
    run = pipeline_run_store.get_run(run_id)
    if run is None:
        return

    estimated_cost_cny = run.estimated_cost_cny
    estimated_duration_seconds = run.estimated_duration_seconds

    pipeline_run_store.update_run_state(run_id, PipelineRunState.RUNNING)
    started_at = time.monotonic()
    try:
        run_episode_pipeline = _load_episode_runner()
        result = run_episode_pipeline(
            episode_id=episode_id,
            source_video=source_video,
            root=root,
        )

        for stage_name in result.get("stages", []):
            stage_result = result.get("stage_results", {}).get(stage_name, {})
            stage_state = str(stage_result.get("state", "unknown"))
            pipeline_run_store.set_stage_state(run_id, stage_name, stage_state)

        actual_duration_seconds = max(0, int(round(time.monotonic() - started_at)))
        if str(result.get("state", "failed")) == "failed":
            pipeline_run_store.update_run_state(
                run_id,
                PipelineRunState.FAILED,
                failed_stage=str(result.get("failed_stage") or ""),
                error_message=str(result.get("error") or "pipeline failed"),
                cost_summary={
                    "estimated_cost_cny": estimated_cost_cny,
                    "estimated_duration_seconds": estimated_duration_seconds,
                    "actual_cost_cny": 0.0,
                    "actual_duration_seconds": actual_duration_seconds,
                },
            )
            return

        pipeline_run_store.update_run_state(
            run_id,
            PipelineRunState.SUCCESS,
            outputs={
                "final_audio_path": str(result["outputs"]["final_audio_path"]),
                "final_video_path": str(result["outputs"]["final_video_path"]),
            },
            cost_summary={
                "estimated_cost_cny": estimated_cost_cny,
                "estimated_duration_seconds": estimated_duration_seconds,
                "actual_cost_cny": estimated_cost_cny,
                "actual_duration_seconds": actual_duration_seconds,
            },
        )
    except Exception as error:
        actual_duration_seconds = max(0, int(round(time.monotonic() - started_at)))
        pipeline_run_store.update_run_state(
            run_id,
            PipelineRunState.FAILED,
            error_message=str(error),
            cost_summary={
                "estimated_cost_cny": estimated_cost_cny,
                "estimated_duration_seconds": estimated_duration_seconds,
                "actual_cost_cny": 0.0,
                "actual_duration_seconds": actual_duration_seconds,
            },
        )


def _serialize_run(run: PipelineRun) -> dict[str, object]:
    return {
        "run_id": run.run_id,
        "episode_id": run.episode_id,
        "source_video": run.source_video,
        "root": run.root,
        "state": run.state.value,
        "stage_states": run.stage_states,
        "failed_stage": run.failed_stage,
        "error_message": run.error_message,
        "estimated_cost_cny": run.estimated_cost_cny,
        "estimated_duration_seconds": run.estimated_duration_seconds,
        "cost_summary": run.cost_summary,
        "final_audio_path": run.outputs.get("final_audio_path", ""),
        "final_video_path": run.outputs.get("final_video_path", ""),
        "created_at": run.created_at.isoformat(),
        "updated_at": run.updated_at.isoformat(),
    }


@router.post("/episodes/{episode_id}/pipeline/run", status_code=202)
def run_episode_pipeline_endpoint(
    episode_id: str,
    payload: RunEpisodePipelineRequest,
    background_tasks: BackgroundTasks,
):
    estimation = estimate_pipeline_cost(payload.source_video)
    run = pipeline_run_store.create_run(
        episode_id=episode_id,
        source_video=payload.source_video,
        root=payload.root,
        estimated_cost_cny=float(estimation["estimated_cost_cny"]),
        estimated_duration_seconds=int(estimation["estimated_duration_seconds"]),
        cost_summary={
            "estimated_cost_cny": float(estimation["estimated_cost_cny"]),
            "estimated_duration_seconds": int(estimation["estimated_duration_seconds"]),
            "actual_cost_cny": 0.0,
            "actual_duration_seconds": 0,
        },
    )
    background_tasks.add_task(
        _execute_pipeline,
        run.run_id,
        episode_id,
        payload.source_video,
        payload.root,
    )
    return {
        "success": True,
        "data": {
            "run_id": run.run_id,
            "episode_id": run.episode_id,
            "state": run.state.value,
            "estimated_cost_cny": run.estimated_cost_cny,
            "estimated_duration_seconds": run.estimated_duration_seconds,
        },
    }


@router.get("/pipeline-runs/{run_id}")
def get_pipeline_run(run_id: str):
    run = pipeline_run_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="pipeline run not found")
    return {"success": True, "data": _serialize_run(run)}


@router.get("/episodes/{episode_id}/pipeline-runs")
def list_episode_pipeline_runs(episode_id: str, limit: int = 20):
    runs = pipeline_run_store.list_runs_by_episode(episode_id, limit=limit)
    return {"success": True, "data": [_serialize_run(item) for item in runs]}
