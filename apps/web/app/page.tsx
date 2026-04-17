"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

type TriggerResponse = {
  success: boolean;
  data?: {
    run_id: string;
    episode_id: string;
    state: string;
    estimated_cost_cny: number;
    estimated_duration_seconds: number;
  };
  error?: string;
};

export default function HomePage() {
  const router = useRouter();

  const [episodeId, setEpisodeId] = useState("episode_1");
  const [sourceVideo, setSourceVideo] = useState("data/input/demo.mkv");
  const [root, setRoot] = useState("data/episodes");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleRun(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/pipeline/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          episode_id: episodeId,
          source_video: sourceVideo,
          root: root.trim() || undefined,
        }),
      });
      const payload = (await response.json()) as TriggerResponse;
      if (!response.ok || !payload.success || !payload.data) {
        setError(payload.error || "创建任务失败，请稍后重试。");
        return;
      }
      router.push(`/runs/${payload.data.run_id}?episode_id=${encodeURIComponent(payload.data.episode_id)}`);
    } catch {
      setError("网络异常，无法连接到本地服务。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header className="hero">
        <span className="hero-eyebrow">AI Dubbing Director Console</span>
        <h1>AI 配音导演台</h1>
        <p>把“创建任务 -> 追踪进度 -> 失败重跑”压缩成一条清晰流程，尽量减少切页和重复操作。</p>
      </header>

      <section className="panel panel-highlight">
        <h2>创建任务</h2>
        <div className="step-row" aria-label="任务操作步骤">
          <span className="step-pill">步骤 1：填写 Episode ID</span>
          <span className="step-pill">步骤 2：提交创建任务</span>
          <span className="step-pill">步骤 3：查看任务历史与详情</span>
        </div>
        <p className="muted">创建后将自动跳转到任务详情页，无需手动查询任务 ID。</p>

        <form className="form-grid" onSubmit={handleRun}>
          <label className="field">
            <span>Episode ID</span>
            <input value={episodeId} onChange={(event) => setEpisodeId(event.target.value)} required />
            <small className="field-hint">建议使用“剧名_集号”命名，方便后续追踪历史任务。</small>
          </label>

          <label className="field">
            <span>源视频路径</span>
            <input value={sourceVideo} onChange={(event) => setSourceVideo(event.target.value)} required />
            <small className="field-hint">支持本地路径（如 `data/input/demo.mkv`）。</small>
          </label>

          <label className="field">
            <span>工作目录（可选）</span>
            <input value={root} onChange={(event) => setRoot(event.target.value)} />
            <small className="field-hint">默认会写入 `data/episodes`。</small>
          </label>

          <button className="run-button" type="submit" disabled={loading || !episodeId || !sourceVideo}>
            {loading ? "创建中..." : "创建任务"}
          </button>
        </form>
        <div className="guide-list">
          <p className="muted">预计处理时长：20-40 分钟（受视频时长、声轨复杂度和重跑次数影响）。</p>
          <p className="muted">路径规范提示：建议统一放在 `data/input` 与 `data/episodes`，便于排障与复用。</p>
        </div>
      </section>

      <section className="panel">
        <h2>快捷入口</h2>
        <p className="muted">
          创建后将自动跳转任务详情。你也可以直接进入历史页，查看同一 Episode 的全部任务。
        </p>
        <p>
          <Link href={`/runs?episode_id=${encodeURIComponent(episodeId)}`}>查看任务历史</Link>
        </p>
      </section>

      {error ? (
        <p className="error" role="alert" aria-live="assertive">
          {error}
        </p>
      ) : null}
    </main>
  );
}
