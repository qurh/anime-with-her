from datetime import UTC, datetime

from app.domain.pipeline_run import PipelineRun, PipelineRunState


class PipelineRunStore:
    def __init__(self):
        self._next_run = 1
        self.runs: dict[str, PipelineRun] = {}

    def create_run(
        self,
        episode_id: str,
        source_video: str,
        root: str,
        estimated_cost_cny: float = 0.0,
        estimated_duration_seconds: int = 0,
        cost_summary: dict[str, float | int] | None = None,
    ) -> PipelineRun:
        run = PipelineRun(
            run_id=f"run_{self._next_run}",
            episode_id=episode_id,
            source_video=source_video,
            root=root,
            estimated_cost_cny=estimated_cost_cny,
            estimated_duration_seconds=estimated_duration_seconds,
            cost_summary=cost_summary or {},
        )
        self._next_run += 1
        self.runs[run.run_id] = run
        return run

    def get_run(self, run_id: str) -> PipelineRun | None:
        return self.runs.get(run_id)

    def update_run_state(
        self,
        run_id: str,
        state: PipelineRunState,
        failed_stage: str | None = None,
        error_message: str | None = None,
        outputs: dict[str, str] | None = None,
        cost_summary: dict[str, float | int] | None = None,
    ) -> PipelineRun:
        run = self.runs[run_id]
        run.state = state
        run.updated_at = datetime.now(UTC)
        if failed_stage is not None:
            run.failed_stage = failed_stage
        if error_message is not None:
            run.error_message = error_message
        if outputs is not None:
            run.outputs = outputs
        if cost_summary is not None:
            run.cost_summary = cost_summary
        return run

    def set_stage_state(self, run_id: str, stage_name: str, stage_state: str) -> PipelineRun:
        run = self.runs[run_id]
        run.stage_states[stage_name] = stage_state
        run.updated_at = datetime.now(UTC)
        return run

    def list_runs_by_episode(self, episode_id: str, limit: int = 20) -> list[PipelineRun]:
        items = [item for item in self.runs.values() if item.episode_id == episode_id]
        items.sort(key=lambda item: int(item.run_id.split("_")[-1]), reverse=True)
        return items[:limit]
