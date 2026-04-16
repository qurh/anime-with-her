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
        <h1>AI 配音导演台</h1>
        <p>三步完成入口：创建任务、查看任务详情、按需重跑失败阶段。</p>
      </header>

      <section className="panel">
        <h2>创建任务</h2>
        <form className="form-grid" onSubmit={handleRun}>
          <label className="field">
            <span>Episode ID</span>
            <input value={episodeId} onChange={(event) => setEpisodeId(event.target.value)} required />
          </label>

          <label className="field">
            <span>源视频路径</span>
            <input value={sourceVideo} onChange={(event) => setSourceVideo(event.target.value)} required />
          </label>

          <label className="field">
            <span>工作目录（可选）</span>
            <input value={root} onChange={(event) => setRoot(event.target.value)} />
          </label>

          <button className="run-button" type="submit" disabled={loading || !episodeId || !sourceVideo}>
            {loading ? "创建中..." : "创建任务"}
          </button>
        </form>
      </section>

      <section className="panel">
        <h2>快速入口</h2>
        <p>
          <Link href={`/runs?episode_id=${encodeURIComponent(episodeId)}`}>查看该 Episode 的任务历史</Link>
        </p>
        <p>
          任务创建成功后会自动跳转到 <code>/runs/&lt;run_id&gt;</code> 详情页。
        </p>
      </section>

      {error ? <p className="error">{error}</p> : null}
    </main>
  );
}
