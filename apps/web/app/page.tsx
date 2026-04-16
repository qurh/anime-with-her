"use client";

import { FormEvent, useMemo, useState } from "react";

type PipelineRunData = {
  episode_id: string;
  state: string;
  stages: string[];
  stage_states: Record<string, string>;
  final_audio_path: string;
  final_video_path: string;
};

type PipelineRunResponse = {
  success: boolean;
  data?: PipelineRunData;
  error?: string;
};

export default function HomePage() {
  const [episodeId, setEpisodeId] = useState("episode_1");
  const [sourceVideo, setSourceVideo] = useState("data/input/demo.mkv");
  const [root, setRoot] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PipelineRunData | null>(null);

  const orderedStageStates = useMemo(() => {
    if (!result) {
      return [];
    }
    return result.stages.map((stageName) => ({
      stageName,
      state: result.stage_states[stageName] || "unknown",
    }));
  }, [result]);

  async function handleRun(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
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
      const payload = (await response.json()) as PipelineRunResponse;
      if (!response.ok || !payload.success || !payload.data) {
        setError(payload.error || "触发失败，请稍后重试。");
        return;
      }
      setResult(payload.data);
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
        <p>从上传素材到中配成片，一键触发整集串跑并实时查看阶段状态。</p>
      </header>

      <section className="panel">
        <h2>整集串跑</h2>
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
            <input value={root} onChange={(event) => setRoot(event.target.value)} placeholder="data/episodes" />
          </label>

          <button className="run-button" type="submit" disabled={loading}>
            {loading ? "串跑中..." : "开始整集串跑"}
          </button>
        </form>
      </section>

      {error ? <p className="error">{error}</p> : null}

      {result ? (
        <section className="panel">
          <h2>运行结果</h2>
          <p>状态：{result.state}</p>
          <p>最终音频：{result.final_audio_path}</p>
          <p>最终视频：{result.final_video_path}</p>
          <div className="stage-list">
            {orderedStageStates.map((item) => (
              <div className="stage-item" key={item.stageName}>
                <strong>{item.stageName}</strong>
                <span>{item.state}</span>
              </div>
            ))}
          </div>
        </section>
      ) : null}
    </main>
  );
}
