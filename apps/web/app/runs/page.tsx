import Link from "next/link";
import { listEpisodePipelineRuns } from "../../lib/api";

type PageProps = {
  searchParams: Promise<{ episode_id?: string }>;
};

export default async function RunsPage({ searchParams }: PageProps) {
  const query = await searchParams;
  const episodeId = (query.episode_id || "episode_1").trim() || "episode_1";
  const runs = await listEpisodePipelineRuns(episodeId, 20);

  return (
    <main className="container">
      <header className="hero">
        <h1>任务历史</h1>
        <p>
          当前 Episode：<strong>{episodeId}</strong>。可进入详情查看阶段状态、失败原因和最终产物。
        </p>
      </header>

      <section className="panel">
        <h2>最近运行记录</h2>
        {runs.length === 0 ? (
          <p>暂无运行记录，请先在首页创建任务。</p>
        ) : (
          <div className="runs-list">
            {runs.map((run) => (
              <article className="run-card" key={run.run_id}>
                <div>
                  <strong>{run.run_id}</strong>
                  <p>
                    状态：{run.state}
                    {run.failed_stage ? `（失败阶段：${run.failed_stage}）` : ""}
                  </p>
                  <p>更新时间：{new Date(run.updated_at).toLocaleString("zh-CN")}</p>
                </div>
                <Link href={`/runs/${run.run_id}?episode_id=${encodeURIComponent(episodeId)}`}>查看详情</Link>
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
