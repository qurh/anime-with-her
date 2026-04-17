import Link from "next/link";
import { listEpisodePipelineRuns, type PipelineRunState, type PipelineRunSummary } from "../../lib/api";

type PageProps = {
  searchParams: Promise<{ episode_id?: string; state?: string; keyword?: string }>;
};

const FILTER_OPTIONS: Array<{ value: "all" | PipelineRunState; label: string }> = [
  { value: "all", label: "全部" },
  { value: "pending", label: "等待中" },
  { value: "running", label: "运行中" },
  { value: "success", label: "已完成" },
  { value: "failed", label: "失败" },
];

function toStatusLabel(state: PipelineRunState): string {
  const mapper: Record<PipelineRunState, string> = {
    pending: "等待中",
    running: "运行中",
    success: "已完成",
    failed: "失败",
  };
  return mapper[state];
}

function toStatusClass(state: PipelineRunState): string {
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

function applyFilters(
  runs: PipelineRunSummary[],
  stateFilter: "all" | PipelineRunState,
  keyword: string,
): PipelineRunSummary[] {
  return runs.filter((run) => {
    if (stateFilter !== "all" && run.state !== stateFilter) {
      return false;
    }
    if (!keyword) {
      return true;
    }
    return run.run_id.toLowerCase().includes(keyword.toLowerCase());
  });
}

export default async function RunsPage({ searchParams }: PageProps) {
  const query = await searchParams;
  const episodeId = (query.episode_id || "episode_1").trim() || "episode_1";
  const stateFilterRaw = (query.state || "all").trim() as "all" | PipelineRunState;
  const stateFilter = FILTER_OPTIONS.some((item) => item.value === stateFilterRaw)
    ? stateFilterRaw
    : "all";
  const keyword = (query.keyword || "").trim();

  const runs = await listEpisodePipelineRuns(episodeId, 20);
  const filteredRuns = applyFilters(runs, stateFilter, keyword);

  const statPending = runs.filter((item) => item.state === "pending").length;
  const statRunning = runs.filter((item) => item.state === "running").length;
  const statFailed = runs.filter((item) => item.state === "failed").length;

  return (
    <main id="main-content" className="container">
      <header className="hero">
        <span className="hero-eyebrow">Run History</span>
        <h1>任务历史</h1>
        <p>
          当前 Episode：<strong>{episodeId}</strong>。可按状态筛选、按任务 ID 搜索，快速定位失败任务并进入详情执行重跑。
        </p>
      </header>

      <section className="panel panel-compact">
        <div className="kpi-row">
          <span className="kpi-chip">总任务：{runs.length}</span>
          <span className="kpi-chip">等待中：{statPending}</span>
          <span className="kpi-chip">运行中：{statRunning}</span>
          <span className="kpi-chip kpi-chip-danger">失败：{statFailed}</span>
        </div>
      </section>

      <section className="panel">
        <form className="filter-grid" action="/runs" method="get">
          <input type="hidden" name="episode_id" value={episodeId} />
          <label className="field">
            <span>状态筛选</span>
            <select name="state" defaultValue={stateFilter}>
              {FILTER_OPTIONS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>搜索任务</span>
            <input name="keyword" defaultValue={keyword} placeholder="输入 run_id 关键字" />
          </label>
          <div className="filter-actions">
            <button className="run-button" type="submit">
              应用筛选
            </button>
            <Link
              className="text-link-muted"
              href={`/runs?episode_id=${encodeURIComponent(episodeId)}`}
            >
              清空
            </Link>
          </div>
        </form>
      </section>

      <section className="panel">
        <h2>最近运行记录</h2>
        {runs.length === 0 ? (
          <div>
            <p>暂无运行记录，请先在首页创建任务。</p>
            <p>
              <Link href="/">返回首页创建任务</Link>
            </p>
          </div>
        ) : filteredRuns.length === 0 ? (
          <div>
            <p>没有匹配的任务，请调整筛选条件后重试。</p>
          </div>
        ) : (
          <div className="runs-list">
            {filteredRuns.map((run) => (
              <article className="run-card" key={run.run_id}>
                <div className="run-card-main">
                  <strong className="mono">{run.run_id}</strong>
                  <p>
                    <span className={toStatusClass(run.state)}>状态：{toStatusLabel(run.state)}</span>
                    {run.failed_stage ? `（失败阶段：${run.failed_stage}）` : ""}
                  </p>
                  <p className="muted">更新时间：{new Date(run.updated_at).toLocaleString("zh-CN")}</p>
                </div>
                <Link className="run-link" href={`/runs/${run.run_id}?episode_id=${encodeURIComponent(episodeId)}`}>
                  查看详情
                </Link>
              </article>
            ))}
          </div>
        )}
      </section>

      <p>
        <Link href="/">返回首页</Link>
      </p>
    </main>
  );
}
