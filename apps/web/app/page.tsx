"use client";

import Link from "next/link";
import { FormEvent, useMemo, useState } from "react";
import { createJob, getJob, JobData, JobState, uploadVideo } from "../lib/api";

const STATE_LABELS: Record<JobState, string> = {
  created: "已创建",
  running: "处理中",
  partial_done: "配音已完成",
  done: "全部完成",
  failed: "处理失败",
  awaiting_budget_decision: "等待预算决策",
  rerendering: "重渲染中",
};

const PIPELINE_STEPS: { key: string; label: string }[] = [
  { key: "created", label: "任务创建" },
  { key: "running", label: "拆分 / ASR / 翻译 / TTS" },
  { key: "partial_done", label: "配音成片产出" },
  { key: "awaiting_budget_decision", label: "预算决策点" },
  { key: "done", label: "口型同步完成" },
];

function formatState(state: JobState): string {
  return STATE_LABELS[state] ?? state;
}

export default function HomePage() {
  const [inputVideo, setInputVideo] = useState("data/input/demo.mp4");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [queryJobId, setQueryJobId] = useState("");
  const [activeJob, setActiveJob] = useState<JobData | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const budgetLink = useMemo(() => {
    const fromCurrent = activeJob?.job_id?.trim();
    const fromInput = queryJobId.trim();
    return `/budget/${fromCurrent || fromInput || "job_1"}`;
  }, [activeJob?.job_id, queryJobId]);

  async function handleCreateJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsCreating(true);
    setError(null);
    setSuccess(null);
    try {
      const job = await createJob(inputVideo.trim());
      setActiveJob(job);
      setQueryJobId(job.job_id);
      setSuccess(`任务 ${job.job_id} 创建成功，可继续查看预算决策。`);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "创建任务失败");
    } finally {
      setIsCreating(false);
    }
  }

  async function handleUploadVideo() {
    if (!selectedFile) {
      setError("请先选择一个视频文件。");
      return;
    }

    setIsUploading(true);
    setError(null);
    setSuccess(null);
    try {
      const uploaded = await uploadVideo(selectedFile);
      setInputVideo(uploaded.stored_path);
      setSuccess(`上传成功：${uploaded.original_filename}，路径已自动填入。`);
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "视频上传失败");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleFetchJob() {
    const id = queryJobId.trim();
    if (!id) {
      setError("请先输入 Job ID。");
      return;
    }
    setIsFetching(true);
    setError(null);
    setSuccess(null);
    try {
      const job = await getJob(id);
      setActiveJob(job);
      setSuccess(`已同步 ${job.job_id} 当前状态。`);
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : "查询任务失败");
    } finally {
      setIsFetching(false);
    }
  }

  const currentState = activeJob?.state ?? "created";

  return (
    <main className="app-shell">
      <section className="glass-bar">
        <div className="brand">
          <div className="brand-badge">A</div>
          <div>
            <h1 className="brand-title">Anime With Her Console</h1>
            <p className="brand-sub">角色级分轨配音工作台</p>
          </div>
        </div>
        <div className="chip-group">
          <span className="chip">Qwen Primary</span>
          <span className="chip">Doubao Fallback</span>
          <span className="chip">角色级分轨</span>
        </div>
      </section>

      <section className="hero">
        <span className="eyebrow">Jobs Command Center</span>
        <h2 className="hero-title">从任务创建到预算决策，一屏把流程跑通。</h2>
        <p className="hero-desc">
          支持直接上传视频并自动回填路径，再创建 Job。默认 10 分钟预算决策窗口，超时自动执行“停掉口型同步，仅完成配音成片”。
        </p>
      </section>

      <section className="metrics">
        <article className="metric-card">
          <p className="metric-label">当前 Job</p>
          <p className="metric-value">{activeJob?.job_id ?? "尚未创建"}</p>
        </article>
        <article className="metric-card">
          <p className="metric-label">当前状态</p>
          <p className="metric-value">{formatState(currentState)}</p>
        </article>
        <article className="metric-card">
          <p className="metric-label">预算超时策略</p>
          <p className="metric-value">默认停口型同步</p>
        </article>
      </section>

      <section className="workspace-grid">
        <article className="panel">
          <h2>创建与追踪任务</h2>
          <p>可先上传视频文件，系统会把生成路径自动填到输入框，再创建 Job。</p>

          <form onSubmit={handleCreateJob}>
            <div className="field">
              <label htmlFor="video-file">上传视频文件</label>
              <input
                id="video-file"
                className="text-input"
                type="file"
                accept="video/*"
                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
              />
            </div>
            <div className="row">
              <button type="button" className="btn btn-soft" onClick={handleUploadVideo} disabled={isUploading}>
                {isUploading ? "上传中..." : "上传视频"}
              </button>
              <span className="notice">{selectedFile ? `已选择：${selectedFile.name}` : "未选择文件"}</span>
            </div>

            <div className="field">
              <label htmlFor="input-video">输入视频路径</label>
              <input
                id="input-video"
                className="text-input"
                value={inputVideo}
                onChange={(event) => setInputVideo(event.target.value)}
                placeholder="data/input/demo.mp4"
              />
            </div>
            <div className="row">
              <button type="submit" className="btn btn-primary" disabled={isCreating}>
                {isCreating ? "创建中..." : "创建 Job"}
              </button>
            </div>
          </form>

          <div className="field">
            <label htmlFor="job-id">查询 Job ID</label>
            <input
              id="job-id"
              className="text-input"
              value={queryJobId}
              onChange={(event) => setQueryJobId(event.target.value)}
              placeholder="job_1"
            />
          </div>
          <div className="row">
            <button className="btn btn-soft" onClick={handleFetchJob} disabled={isFetching}>
              {isFetching ? "同步中..." : "同步状态"}
            </button>
            <Link href={budgetLink} className="btn btn-soft">
              打开预算决策页
            </Link>
          </div>

          {error ? <div className="error">{error}</div> : null}
          {success ? <div className="success">{success}</div> : null}

          {activeJob ? (
            <div className="status-box">
              <span className={`status-pill status-${activeJob.state}`}>{formatState(activeJob.state)}</span>
              <p>Job ID: {activeJob.job_id}</p>
              <p>输入视频: {activeJob.input_video ?? "未提供"}</p>
            </div>
          ) : null}
        </article>

        <article className="panel">
          <h3>流程可视化</h3>
          <p>每个阶段可独立重跑，角色音色可后置人工替换并整片重渲染。</p>
          <div className="steps">
            {PIPELINE_STEPS.map((step) => (
              <div key={step.key} className="step-item">
                <span className="step-name">{step.label}</span>
                <span className="step-state">{step.key === currentState ? "当前阶段" : "待执行 / 已经过"}</span>
              </div>
            ))}
          </div>
          <div className="notice">Jobs 流程现在支持“上传 -&gt; 创建 -&gt; 查询 -&gt; 预算决策”一条龙操作。</div>
        </article>
      </section>
    </main>
  );
}
