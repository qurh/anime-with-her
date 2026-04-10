"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, useMemo, useRef, useState } from "react";
import { createJob, JobData, JobState, uploadVideo } from "../lib/api";

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

function toFriendlyError(error: unknown, fallback: string): string {
  if (error instanceof Error) {
    if (error.message.includes("Failed to fetch")) {
      return "网络请求失败。请确认后端已启动，并允许来自 3000 端口的跨域访问。";
    }
    return error.message;
  }
  return fallback;
}

export default function HomePage() {
  const [inputVideo, setInputVideo] = useState("");
  const [hasUploadedVideo, setHasUploadedVideo] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [lastUploadedFile, setLastUploadedFile] = useState<string | null>(null);
  const [activeJob, setActiveJob] = useState<JobData | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const budgetLink = useMemo(() => {
    return `/budget/${activeJob?.job_id || "job_1"}`;
  }, [activeJob?.job_id]);

  async function handleCreateJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!hasUploadedVideo || !inputVideo.trim()) {
      setError("请先上传视频文件，再创建 Job。");
      setSuccess(null);
      return;
    }
    setIsCreating(true);
    setError(null);
    setSuccess(null);
    try {
      const job = await createJob(inputVideo.trim());
      setActiveJob(job);
      setSuccess(`任务 ${job.job_id} 创建成功，可继续查看预算决策。`);
    } catch (createError) {
      setError(toFriendlyError(createError, "创建任务失败"));
    } finally {
      setIsCreating(false);
    }
  }

  async function handleSelectAndUpload(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) {
      return;
    }

    setIsUploading(true);
    setError(null);
    setSuccess(null);
    try {
      const uploaded = await uploadVideo(selectedFile);
      setInputVideo(uploaded.stored_path);
      setHasUploadedVideo(true);
      setLastUploadedFile(uploaded.original_filename);
      setSuccess(`上传成功：${uploaded.original_filename}`);
    } catch (uploadError) {
      setError(toFriendlyError(uploadError, "视频上传失败"));
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  const currentState = activeJob?.state ?? "created";
  const steps = [
    { label: "上传视频", done: hasUploadedVideo, current: !hasUploadedVideo },
    { label: "创建 Job", done: Boolean(activeJob), current: hasUploadedVideo && !activeJob },
    { label: "预算决策", done: false, current: Boolean(activeJob) },
  ];

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
        <h2 className="hero-title">先上传，后创建，再决策。三步完成配音任务入口。</h2>
        <p className="hero-desc">
          适用于“角色级分轨 + 快速出片优先”场景。你在首屏就能完成核心操作，无需切换页面和手工填写路径。
        </p>
      </section>

      <section className="metrics">
        <article className="metric-card">
          <p className="metric-label">当前阶段</p>
          <p className="metric-value">{activeJob ? "已创建任务" : hasUploadedVideo ? "等待创建 Job" : "等待上传"}</p>
        </article>
        <article className="metric-card">
          <p className="metric-label">任务状态</p>
          <p className="metric-value">{formatState(currentState)}</p>
        </article>
        <article className="metric-card">
          <p className="metric-label">默认预算策略</p>
          <p className="metric-value">默认停口型同步</p>
        </article>
      </section>

      <section className="workspace-grid">
        <article className="panel">
          <h2>创建任务</h2>
          <p>只保留必要操作，降低误操作。按下面步骤顺序执行即可。</p>

          <div className="flow-steps">
            {steps.map((step, index) => (
              <div
                key={step.label}
                className={`flow-step${step.done ? " done" : ""}${step.current ? " current" : ""}`}
              >
                <span className="flow-index">{index + 1}</span>
                <span>{step.label}</span>
              </div>
            ))}
          </div>

          <form onSubmit={handleCreateJob}>
            <div className="field">
              <label htmlFor="video-file">上传视频文件</label>
              <div className="upload-compact">
                <input
                  id="video-file"
                  ref={fileInputRef}
                  className="sr-only-input"
                  type="file"
                  accept="video/*"
                  onChange={handleSelectAndUpload}
                />
                <button type="button" className="btn btn-soft" onClick={openFilePicker} disabled={isUploading}>
                  {isUploading ? "上传中..." : "选择并上传视频"}
                </button>
                <span className="notice">
                  {isUploading
                    ? "正在上传，请稍候..."
                    : lastUploadedFile
                    ? `最近上传：${lastUploadedFile}`
                    : "选择文件后自动上传并回填路径"}
                </span>
              </div>
              <p className="notice">当前使用路径：{inputVideo || "尚未上传"}</p>
            </div>

            <div className="row">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isCreating || isUploading || !hasUploadedVideo}
              >
                {isCreating ? "创建中..." : hasUploadedVideo ? "创建 Job" : "请先上传视频"}
              </button>
              {activeJob ? (
                <Link href={budgetLink} className="btn btn-soft">
                  打开预算决策页
                </Link>
              ) : null}
            </div>
          </form>

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
          <h3>下一步建议</h3>
          <p>创建任务后，优先进入预算决策页，确认是否继续口型同步。</p>
          <div className="next-card">
            <p className="metric-label">推荐操作</p>
            <p className="metric-value">{activeJob ? "进入预算决策" : "先上传并创建 Job"}</p>
            {activeJob ? (
              <Link href={budgetLink} className="btn btn-soft">
                前往预算决策页
              </Link>
            ) : (
              <p className="notice">当前还没有 Job，完成上传并创建后会自动解锁。</p>
            )}
          </div>

          <p>流程可视化</p>
          <div className="steps">
            {PIPELINE_STEPS.map((step) => (
              <div key={step.key} className="step-item">
                <span className="step-name">{step.label}</span>
                <span className="step-state">{step.key === currentState ? "当前阶段" : "待执行 / 已经过"}</span>
              </div>
            ))}
          </div>

          <details className="ux-details">
            <summary>为什么这样设计</summary>
            <ul className="muted-list">
              <li>首屏就可操作：上传和创建都在同一屏完成。</li>
              <li>减少决策成本：移除手工查询入口，保持单主任务。</li>
              <li>提供即时反馈：上传、创建、错误都有明确状态提示。</li>
            </ul>
          </details>
        </article>
      </section>
    </main>
  );
}
