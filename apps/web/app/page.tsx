"use client";

import Link from "next/link";
import { ChangeEvent, FormEvent, useMemo, useRef, useState } from "react";
import { createJob, JobData, JobState, uploadVideo } from "../lib/api";

const STATE_LABELS: Record<JobState, string> = {
  created: "已创建",
  running: "处理中",
  partial_done: "配音成片已输出",
  done: "全部完成",
  failed: "处理失败",
  awaiting_budget_decision: "等待预算决策",
  rerendering: "重渲染中",
};

function formatState(state: JobState): string {
  return STATE_LABELS[state] ?? state;
}

function toFriendlyError(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.includes("Failed to fetch")) {
    return "网络请求失败，请确认后端已启动，并允许来自 3000 端口的跨域访问。";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
}

export default function HomePage() {
  const [inputVideo, setInputVideo] = useState("");
  const [hasUploadedVideo, setHasUploadedVideo] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [activeJob, setActiveJob] = useState<JobData | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const budgetLink = useMemo(() => `/budget/${activeJob?.job_id || "job_1"}`, [activeJob?.job_id]);

  async function handleCreateJob(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!hasUploadedVideo || !inputVideo.trim()) {
      setError("请先上传视频，再创建任务。");
      setSuccess(null);
      return;
    }

    setIsCreating(true);
    setError(null);
    setSuccess(null);

    try {
      const job = await createJob(inputVideo.trim());
      setActiveJob(job);
      setSuccess(`任务 ${job.job_id} 创建成功。`);
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
      setSuccess(`上传成功：${uploaded.original_filename}`);
    } catch (uploadError) {
      setError(toFriendlyError(uploadError, "视频上传失败"));
    } finally {
      setIsUploading(false);
      event.target.value = "";
    }
  }

  return (
    <main className="app-shell">
      <section className="glass-bar compact">
        <div className="brand">
          <div className="brand-badge">配</div>
          <div>
            <h1 className="brand-title">动漫中配工作台</h1>
            <p className="brand-sub">保留原音色、原情绪，生成高质量中配</p>
          </div>
        </div>
      </section>

      <section className="hero gentle">
        <h2 className="hero-title">把优秀外语动漫，转化为原音色原情绪的中配版本。</h2>
      </section>

      <section className="workspace-grid">
        <article className="panel">
          <h2>创建任务</h2>

          <div className="flow-steps">
            <div className={`flow-step${hasUploadedVideo ? " done" : " current"}`}>
              <span className="flow-index">1</span>
              <span>上传视频</span>
            </div>
            <div className={`flow-step${activeJob ? " done" : hasUploadedVideo ? " current" : ""}`}>
              <span className="flow-index">2</span>
              <span>创建任务</span>
            </div>
            <div className={`flow-step${activeJob ? " current" : ""}`}>
              <span className="flow-index">3</span>
              <span>预算决策</span>
            </div>
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
                <button
                  type="button"
                  className="btn btn-soft"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  {isUploading ? "上传中..." : "选择并上传视频"}
                </button>
              </div>
            </div>

            <div className="row">
              <button type="submit" className="btn btn-primary" disabled={isCreating || isUploading || !hasUploadedVideo}>
                {isCreating ? "创建中..." : "创建任务"}
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
        </article>

        <article className="panel">
          <h3>任务状态</h3>
          {!activeJob ? (
            <p>还没有任务。完成上传并点击“创建任务”后，这里会显示状态与下一步入口。</p>
          ) : (
            <>
              <div className="status-box">
                <span className={`status-pill status-${activeJob.state}`}>{formatState(activeJob.state)}</span>
                <p>Job ID: {activeJob.job_id}</p>
                <p>输入视频: {activeJob.input_video ?? "未提供"}</p>
              </div>
              <div className="next-card">
                <p className="metric-label">下一步</p>
                <p className="metric-value">进入预算决策</p>
                <Link href={budgetLink} className="btn btn-soft">
                  前往预算决策页
                </Link>
              </div>
            </>
          )}
        </article>
      </section>
    </main>
  );
}
