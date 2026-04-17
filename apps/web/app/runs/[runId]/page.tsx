"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

type PipelineRunDetail = {
  run_id: string;
  episode_id: string;
  source_video: string;
  root: string;
  state: "pending" | "running" | "success" | "failed";
  stage_states: Record<string, string>;
  failed_stage: string | null;
  error_message: string | null;
  final_audio_path: string;
  final_video_path: string;
  estimated_cost_cny: number;
  estimated_duration_seconds: number;
};

type Envelope<T> = {
  success: boolean;
  data?: T;
  error?: string;
};

type StageState = "pending" | "running" | "success" | "failed";

const STAGE_ORDER = [
  "media_ingest",
  "audio_separation",
  "asr_align",
  "speaker_role",
  "dub_script",
  "tts_synthesis",
  "mix_master",
];

function toStateLabel(state: string): string {
  const mapper: Record<string, string> = {
    pending: "等待中",
    running: "运行中",
    success: "已完成",
    failed: "失败",
  };
  return mapper[state] || "未知";
}

function toStateClass(state: string): string {
  if (state === "success") {
    return "status-badge status-badge-success";
  }
  if (state === "failed") {
    return "status-badge status-badge-danger";
  }
  if (state === "running") {
    return "status-badge status-badge-info";
  }
  return "status-badge";
}

export default function RunDetailPage() {
  const params = useParams<{ runId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const runId = params.runId;
  const episodeIdQuery = searchParams.get("episode_id") || "";

  const [run, setRun] = useState<PipelineRunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retryStage, setRetryStage] = useState("tts_synthesis");
  const [retrying, setRetrying] = useState(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState("");
  const [onlyFailedStages, setOnlyFailedStages] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    async function pullRunStatus() {
      try {
        const response = await fetch(`/api/pipeline/runs/${encodeURIComponent(runId)}`, { cache: "no-store" });
        const payload = (await response.json()) as Envelope<PipelineRunDetail>;
        if (!response.ok || !payload.success || !payload.data) {
          throw new Error(payload.error || "任务详情获取失败。");
        }
        if (cancelled) {
          return;
        }
        setRun(payload.data);
        setRetryStage(payload.data.failed_stage || "tts_synthesis");
        setLastRefreshedAt(new Date().toLocaleString("zh-CN"));
        setError("");
        if (payload.data.state === "pending" || payload.data.state === "running") {
          timer = setTimeout(pullRunStatus, 2000);
        }
      } catch (pullError) {
        if (!cancelled) {
          setError(pullError instanceof Error ? pullError.message : "任务详情获取失败。");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void pullRunStatus();
    return () => {
      cancelled = true;
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [runId]);

  const orderedStageStates = useMemo(() => {
    if (!run) {
      return [] as Array<{ stage: string; state: StageState }>;
    }
    const keys = Object.keys(run.stage_states);
    const merged = [...STAGE_ORDER, ...keys.filter((key) => !STAGE_ORDER.includes(key))];
    return merged.map((stage) => ({
      stage,
      state: (run.stage_states[stage] || "pending") as StageState,
    }));
  }, [run]);

  const stageSummary = useMemo(() => {
    const summary = { total: orderedStageStates.length, success: 0, failed: 0, running: 0, pending: 0 };
    for (const item of orderedStageStates) {
      if (item.state === "success") summary.success += 1;
      else if (item.state === "failed") summary.failed += 1;
      else if (item.state === "running") summary.running += 1;
      else summary.pending += 1;
    }
    return summary;
  }, [orderedStageStates]);

  const visibleStages = useMemo(() => {
    if (!onlyFailedStages) {
      return orderedStageStates;
    }
    return orderedStageStates.filter((item) => item.state === "failed");
  }, [onlyFailedStages, orderedStageStates]);

  async function handleRetry(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!run) {
      return;
    }

    setRetrying(true);
    setError("");
    try {
      const response = await fetch("/api/pipeline/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          episode_id: run.episode_id,
          source_video: run.source_video,
          root: run.root,
          start_stage: retryStage,
        }),
      });
      const payload = (await response.json()) as Envelope<{ run_id: string }>;
      if (!response.ok || !payload.success || !payload.data) {
        throw new Error(payload.error || "重跑触发失败。");
      }
      router.push(`/runs/${payload.data.run_id}?episode_id=${encodeURIComponent(run.episode_id)}`);
    } catch (retryError) {
      setError(retryError instanceof Error ? retryError.message : "重跑触发失败。");
    } finally {
      setRetrying(false);
    }
  }

  return (
    <main className="container">
      <header className="hero">
        <span className="hero-eyebrow">Run Detail</span>
        <h1>任务详情</h1>
        <p>
          任务 ID：<span className="mono">{runId}</span>
        </p>
      </header>

      {loading ? <p aria-live="polite">加载中（运行中任务每 2 秒刷新）...</p> : null}
      {error ? (
        <p className="error" role="alert" aria-live="assertive">
          {error}
        </p>
      ) : null}

      {run ? (
        <>
          <section className="panel">
            <h2>总体状态</h2>
            <div className="meta-grid">
              <p>
                任务状态：<span className={toStateClass(run.state)}>{toStateLabel(run.state)}</span>
              </p>
              <p>Episode ID：{run.episode_id}</p>
              <p>源视频路径：{run.source_video}</p>
              <p>预估成本：￥{run.estimated_cost_cny.toFixed(2)}</p>
              <p>预估时长：{run.estimated_duration_seconds}s</p>
              <p>上次刷新时间：{lastRefreshedAt || "尚未刷新"}</p>
              {run.failed_stage ? <p>失败阶段：{run.failed_stage}</p> : null}
            </div>
            {run.error_message ? <p className="error">失败原因：{run.error_message}</p> : null}
          </section>

          <section className="panel">
            <div className="stage-header-row">
              <h2>阶段状态</h2>
              <button
                className="run-button run-button-secondary"
                type="button"
                onClick={() => setOnlyFailedStages((value) => !value)}
              >
                {onlyFailedStages ? "查看全部阶段" : "仅看异常阶段"}
              </button>
            </div>
            <div className="kpi-row" aria-label="阶段摘要">
              <span className="kpi-chip">阶段摘要：共 {stageSummary.total} 个</span>
              <span className="kpi-chip">已完成：{stageSummary.success}</span>
              <span className="kpi-chip">运行中：{stageSummary.running}</span>
              <span className="kpi-chip">等待中：{stageSummary.pending}</span>
              <span className="kpi-chip kpi-chip-danger">失败：{stageSummary.failed}</span>
            </div>
            <div className="stage-list">
              {visibleStages.length === 0 ? (
                <p className="muted">当前没有异常阶段。</p>
              ) : (
                visibleStages.map((item) => (
                  <div className="stage-item" key={item.stage}>
                    <strong className="mono">{item.stage}</strong>
                    <span className={toStateClass(item.state)}>{toStateLabel(item.state)}</span>
                  </div>
                ))
              )}
            </div>
          </section>

          <section className="panel">
            <h2>最终产物</h2>
            <p>
              最终音频：<span className="mono">{run.final_audio_path || "尚未产出"}</span>
            </p>
            <p>
              最终视频：<span className="mono">{run.final_video_path || "尚未产出"}</span>
            </p>
          </section>

          {run.state === "failed" ? (
            <section className="panel panel-highlight">
              <h2>从失败阶段重跑</h2>
              <p className="muted">重跑起点会写入 `start_stage`，并创建一个新的任务记录。</p>
              <form className="form-grid" onSubmit={handleRetry}>
                <label className="field">
                  <span>start_stage（重跑起点）</span>
                  <select value={retryStage} onChange={(event) => setRetryStage(event.target.value)}>
                    {STAGE_ORDER.map((stage) => (
                      <option key={stage} value={stage}>
                        {stage}
                      </option>
                    ))}
                  </select>
                </label>
                <button className="run-button" type="submit" disabled={retrying}>
                  {retrying ? "重跑提交中..." : "提交重跑"}
                </button>
              </form>
            </section>
          ) : null}
        </>
      ) : null}

      <p>
        <Link href={episodeIdQuery ? `/runs?episode_id=${encodeURIComponent(episodeIdQuery)}` : "/runs"}>
          返回任务历史
        </Link>
      </p>
      <p>
        <Link href="/">返回首页</Link>
      </p>
    </main>
  );
}
