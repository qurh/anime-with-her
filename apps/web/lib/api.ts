export const API_BASE_URL = process.env.BACKEND_BASE_URL || "http://127.0.0.1:8000";

export type PipelineRunState = "pending" | "running" | "success" | "failed";

export type PipelineRunSummary = {
  run_id: string;
  episode_id: string;
  state: PipelineRunState;
  created_at: string;
  updated_at: string;
  failed_stage: string | null;
};

export type PipelineRunDetail = PipelineRunSummary & {
  source_video: string;
  root: string;
  stage_states: Record<string, string>;
  error_message: string | null;
  final_audio_path: string;
  final_video_path: string;
  estimated_cost_cny: number;
  estimated_duration_seconds: number;
  cost_summary: Record<string, number>;
};

export type TriggerPipelineRunRequest = {
  episode_id: string;
  source_video: string;
  root?: string;
  start_stage?: string;
};

export type TriggerPipelineRunResult = {
  run_id: string;
  episode_id: string;
  state: PipelineRunState;
  estimated_cost_cny: number;
  estimated_duration_seconds: number;
};

type BackendEnvelope<T> = {
  success: boolean;
  data?: T;
  error?: string;
};

async function requestBackend<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, cache: "no-store" });
  const payload = (await response.json()) as BackendEnvelope<T>;
  if (!response.ok || !payload.success || payload.data === undefined) {
    throw new Error(payload.error || "后端请求失败。");
  }
  return payload.data;
}

export async function triggerPipelineRun(payload: TriggerPipelineRunRequest): Promise<TriggerPipelineRunResult> {
  return requestBackend<TriggerPipelineRunResult>(
    `/api/v1/episodes/${encodeURIComponent(payload.episode_id)}/pipeline/run`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_video: payload.source_video,
        root: payload.root,
        start_stage: payload.start_stage,
      }),
    },
  );
}

export async function fetchPipelineRun(runId: string): Promise<PipelineRunDetail> {
  return requestBackend<PipelineRunDetail>(`/api/v1/pipeline-runs/${encodeURIComponent(runId)}`);
}

export async function listEpisodePipelineRuns(
  episodeId: string,
  limit = 20,
): Promise<PipelineRunSummary[]> {
  const query = `?limit=${encodeURIComponent(String(limit))}`;
  return requestBackend<PipelineRunSummary[]>(
    `/api/v1/episodes/${encodeURIComponent(episodeId)}/pipeline-runs${query}`,
  );
}
