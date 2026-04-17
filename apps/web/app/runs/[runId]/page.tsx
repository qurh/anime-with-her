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

const STAGE_ORDER = [
  "media_ingest",
  "audio_separation",
  "asr_align",
  "speaker_role",
  "dub_script",
  "tts_synthesis",
  "mix_master",
];

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
      return [];
    }
    const keys = Object.keys(run.stage_states);
    const merged = [...STAGE_ORDER, ...keys.filter((key) => !STAGE_ORDER.includes(key))];
    return merged.map((stage) => ({ stage, state: run.stage_states[stage] || "pending" }));
  }, [run]);

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
        <h1>任务详情</h1>
        <p>任务 ID：{runId}</p>
      </header>

      {loading ? <p>加载中...</p> : null}
      {error ? <p className="error">{error}</p> : null}

      {run ? (
        <>
          <section className="panel">
            <h2>总体状态</h2>
            <p>任务状态：{run.state}</p>
            <p>Episode ID：{run.episode_id}</p>
            <p>源视频路径：{run.source_video}</p>
            <p>预估成本：¥{run.estimated_cost_cny.toFixed(2)}</p>
            <p>预估时长：{run.estimated_duration_seconds}s</p>
            {run.error_message ? <p className="error">失败原因：{run.error_message}</p> : null}
          </section>

          <section className="panel">
            <h2>阶段状态</h2>
            <div className="stage-list">
              {orderedStageStates.map((item) => (
                <div className="stage-item" key={item.stage}>
                  <strong>{item.stage}</strong>
                  <span>{item.state}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="panel">
            <h2>最终产物</h2>
            <p>最终音频：{run.final_audio_path || "尚未产出"}</p>
            <p>最终视频：{run.final_video_path || "尚未产出"}</p>
          </section>

          {run.state === "failed" ? (
            <section className="panel">
              <h2>从失败阶段重跑</h2>
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
