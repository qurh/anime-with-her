"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { BudgetDecisionData, getBudgetDecision } from "../../../lib/api";

type BudgetDecisionClientPageProps = {
  jobId: string;
};

function presentOptionLabel(option: string): string {
  if (option === "skip_lipsync_continue_dubbing") {
    return "停掉口型同步，仅完成配音成片";
  }
  if (option === "continue_full_pipeline") {
    return "继续完整流程（包含口型同步）";
  }
  return option;
}

function presentOptionDesc(option: string): string {
  if (option === "skip_lipsync_continue_dubbing") {
    return "最快拿到可交付版本，成本可控，适合预算敏感场景。";
  }
  if (option === "continue_full_pipeline") {
    return "获得更高一致性的完整成片，但会继续消耗额外预算。";
  }
  return "按当前策略执行。";
}

export default function BudgetDecisionClientPage({ jobId }: BudgetDecisionClientPageProps) {
  const [data, setData] = useState<BudgetDecisionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const decision = await getBudgetDecision(jobId);
        if (!active) {
          return;
        }
        setData(decision);
        setSelected(decision.default_action);
      } catch (fetchError) {
        if (!active) {
          return;
        }
        setError(fetchError instanceof Error ? fetchError.message : "获取预算决策失败");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, [jobId]);

  const options = useMemo(() => data?.options ?? [], [data?.options]);

  return (
    <main className="app-shell budget-shell">
      <section className="glass-bar">
        <div className="brand">
          <div className="brand-badge">B</div>
          <div>
            <h1 className="brand-title">Budget Decision</h1>
            <p className="brand-sub">预算决策与默认回退策略</p>
          </div>
        </div>
        <div className="chip-group">
          <span className="chip">Job: {jobId}</span>
          <span className="chip">10 分钟超时窗口</span>
        </div>
      </section>

      <section className="panel budget-header">
        <h2>预算决策面板</h2>
        <p>当口型同步成本超预算时，请在窗口期内选择策略。未选择时将执行默认动作。</p>
        <Link href="/" className="small-link">
          返回 Jobs 控制台
        </Link>
      </section>

      <section className="panel">
        {loading ? <p>正在加载预算信息...</p> : null}
        {error ? <div className="error">{error}</div> : null}

        {data ? (
          <>
            <div className="metrics">
              <article className="metric-card">
                <p className="metric-label">Job ID</p>
                <p className="metric-value">{data.job_id}</p>
              </article>
              <article className="metric-card">
                <p className="metric-label">预计继续消耗</p>
                <p className="metric-value">¥ {data.estimated_extra_cost_cny.toFixed(2)}</p>
              </article>
              <article className="metric-card">
                <p className="metric-label">决策超时</p>
                <p className="metric-value">{data.timeout_minutes} 分钟</p>
              </article>
            </div>

            <div className="budget-grid">
              {options.map((option) => {
                const isDefault = option === data.default_action;
                const isSelected = option === selected;
                return (
                  <article
                    key={option}
                    className={`budget-card${isDefault ? " default" : ""}`}
                    onClick={() => setSelected(option)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        setSelected(option);
                      }
                    }}
                  >
                    <strong>{presentOptionLabel(option)}</strong>
                    <p>{presentOptionDesc(option)}</p>
                    <p className="notice">
                      {isDefault ? "默认策略" : "可选策略"} · {isSelected ? "当前选中" : "点击选择"}
                    </p>
                  </article>
                );
              })}
            </div>

            <div className="status-box">
              <span className="status-pill status-awaiting_budget_decision">建议确认策略后再执行</span>
              <p>当前选择：{selected ? presentOptionLabel(selected) : "未选择"}</p>
              <p>默认动作：{presentOptionLabel(data.default_action)}</p>
            </div>
          </>
        ) : null}
      </section>
    </main>
  );
}
