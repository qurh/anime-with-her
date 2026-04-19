import type { Page } from "@playwright/test";

type RunState = "pending" | "running" | "success" | "failed";

type MockRunDetail = {
  run_id: string;
  episode_id: string;
  source_video: string;
  root: string;
  state: RunState;
  stage_states: Record<string, string>;
  failed_stage: string | null;
  error_message: string | null;
  final_audio_path: string;
  final_video_path: string;
  estimated_cost_cny: number;
  estimated_duration_seconds: number;
  cost_summary: Record<string, number>;
  qa_summary: Record<string, unknown>;
  warnings: string[];
};

const BASE_STAGE_STATES: Record<string, string> = {
  media_ingest: "success",
  audio_separation: "success",
  asr_align: "success",
  speaker_role: "success",
  dub_script: "success",
  tts_synthesis: "failed",
  mix_master: "pending",
};

function buildRunDetail(runId: string): MockRunDetail {
  if (runId === "run_101") {
    return {
      run_id: "run_101",
      episode_id: "episode_1",
      source_video: "data/input/demo.mkv",
      root: "data/episodes",
      state: "success",
      stage_states: {
        ...BASE_STAGE_STATES,
        tts_synthesis: "success",
        mix_master: "success",
      },
      failed_stage: null,
      error_message: null,
      final_audio_path: "data/episodes/episode_1/output/final_audio_mix.wav",
      final_video_path: "data/episodes/episode_1/output/final_dubbed.mp4",
      estimated_cost_cny: 6.4,
      estimated_duration_seconds: 1320,
      cost_summary: {
        estimated_cost_cny: 6.4,
        estimated_duration_seconds: 1320,
        actual_cost_cny: 5.9,
        actual_duration_seconds: 1180,
      },
      qa_summary: {
        timing_fit_score: 0.92,
        voice_stability_score: 0.9,
        mix_balance_score: 0.88,
        threshold_flags: {
          timing_fit_score: { is_below_threshold: false, reason: "时序匹配良好" },
          voice_stability_score: { is_below_threshold: false, reason: "音色稳定" },
          mix_balance_score: { is_below_threshold: false, reason: "混音平衡达标" },
        },
      },
      warnings: [],
    };
  }

  return {
    run_id: "run_100",
    episode_id: "episode_1",
    source_video: "data/input/demo.mkv",
    root: "data/episodes",
    state: "failed",
    stage_states: BASE_STAGE_STATES,
    failed_stage: "tts_synthesis",
    error_message: "mock tts timeout",
    final_audio_path: "",
    final_video_path: "",
    estimated_cost_cny: 6.4,
    estimated_duration_seconds: 1320,
    cost_summary: {
      estimated_cost_cny: 6.4,
      estimated_duration_seconds: 1320,
      actual_cost_cny: 2.1,
      actual_duration_seconds: 420,
    },
    qa_summary: {
      timing_fit_score: 0.73,
      voice_stability_score: 0.62,
      mix_balance_score: 0.7,
      threshold_flags: {
        voice_stability_score: { is_below_threshold: true, reason: "合成抖动偏高" },
      },
    },
    warnings: ["tts_synthesis: provider timeout"],
  };
}

export async function installMockPipelineApi(page: Page): Promise<void> {
  await page.route("**/api/pipeline/run", async (route) => {
    const request = route.request();
    if (request.method() !== "POST") {
      await route.continue();
      return;
    }

    const body = request.postDataJSON() as Record<string, unknown>;
    const hasRetryStage = typeof body.start_stage === "string" && body.start_stage.length > 0;

    const runId = hasRetryStage ? "run_101" : "run_100";

    await route.fulfill({
      status: 202,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          run_id: runId,
          episode_id: "episode_1",
          state: "pending",
          estimated_cost_cny: 6.4,
          estimated_duration_seconds: 1320,
        },
      }),
    });
  });

  await page.route("**/api/pipeline/runs/*", async (route) => {
    const request = route.request();
    if (request.method() !== "GET") {
      await route.continue();
      return;
    }

    const url = new URL(request.url());
    const runId = url.pathname.split("/").pop() || "run_100";

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: buildRunDetail(runId),
      }),
    });
  });
}
