# Director Console Phase 3 Execution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将项目从“Phase 2 + UI/UX 收口”推进到“真实能力可控接入 + 质量评估增强 + 交互回归可自动化”的 Phase 3 可交付状态。

**Architecture:** 保持现有 `backend + worker + web` 单体 monorepo 结构与 API 契约不破坏，在 worker 适配层引入真实实现（可降级 fake），在 backend 与 web 暴露可诊断字段，并补齐 Playwright 交互回归。所有任务严格走 TDD：先失败测试，再最小实现，再回归通过。

**Tech Stack:** Python 3.12, FastAPI, pytest, Next.js 15, React 19, TypeScript, Playwright, ffmpeg, 可插拔第三方 TTS/ASR/Diarization 适配器。

## 0. Priority / 人天 / 风险矩阵

| ID | Task | Priority | Estimate (人天) | 风险等级 | 主要风险 |
|---|---|---|---:|---|---|
| T1 | TTS 真实调用稳定化（超时/重试/降级） | P0 | 1.5 | 中 | 供应商 API 抖动与密钥管理 |
| T2 | ASR 真实适配接入（可回退） | P0 | 2.0 | 高 | 本地依赖复杂、性能波动 |
| T3 | Speaker Role 真实适配接入（可回退） | P0 | 2.5 | 高 | 分离质量与聚类稳定性 |
| T4 | QA 指标从“常量”升级为“产物驱动” | P0 | 1.0 | 中 | 指标定义与阈值争议 |
| T5 | Backend 扩展运行态诊断字段 | P0 | 1.0 | 低 | 向后兼容字段语义 |
| T6 | Web 展示 QA/告警/成本诊断 | P1 | 1.0 | 低 | 信息密度增加导致可读性下降 |
| T7 | Playwright 主流程交互回归 | P0 | 1.5 | 中 | 测试稳定性与等待策略 |
| T8 | 长流程手工验收与文档收口 | P1 | 0.5 | 低 | 环境不一致导致复现困难 |

总计：11.0 人天（单人）。若并行 2 人可压缩到约 6-7 个工作日。

## 1. 执行前约束

- 必须先执行 `@superpowers:test-driven-development`。
- 每个任务完成后执行最小回归并提交一个 commit。
- 任何真实适配器失败时必须 fallback 到 fake 并输出可读 `warnings`。
- 不修改现有对外接口路径，仅扩展字段。

## 2. 实施任务

### Task 1 (T1): TTS 真实调用稳定化（超时/重试/降级）

**Files:**
- Modify: `apps/worker/worker/adapters/tts_provider.py`
- Modify: `apps/worker/worker/adapters/tts_synthesis.py`
- Modify: `tests/unit/test_tts_provider_live_contract.py`
- Create: `tests/unit/test_tts_provider_resilience.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_tts_provider_resilience.py
def test_live_tts_timeout_triggers_fallback(monkeypatch):
    ...
    assert result["provider"] == "doubao_tts"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_tts_provider_resilience.py -v`
Expected: FAIL with timeout/retry behavior missing.

**Step 3: Write minimal implementation**

```python
# in tts_provider.py
for attempt in range(max_retries):
    try:
        return _invoke_live_tts(...)
    except TimeoutError:
        if attempt == max_retries - 1:
            raise
```

- 新增环境变量：`TTS_TIMEOUT_MS`, `TTS_MAX_RETRIES`。
- 主供应商失败时继续走现有 fallback provider。

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_tts_provider_live_contract.py tests/unit/test_tts_provider_resilience.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker/worker/adapters/tts_provider.py apps/worker/worker/adapters/tts_synthesis.py tests/unit/test_tts_provider_live_contract.py tests/unit/test_tts_provider_resilience.py
git commit -m "feat(worker): harden live tts with timeout retry and fallback"
```

### Task 2 (T2): ASR 真实适配接入（可回退）

**Files:**
- Modify: `apps/worker/worker/adapters/asr_align.py`
- Modify: `apps/worker/worker/config.py`
- Modify: `tests/unit/test_asr_align_adapter.py`
- Create: `tests/unit/test_asr_align_real_adapter.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_asr_align_real_adapter.py
def test_asr_real_mode_uses_live_path_when_model_available(monkeypatch, tmp_path):
    ...
    assert result["execution_mode"] == "real"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_asr_align_real_adapter.py -v`
Expected: FAIL because real-path does not exist.

**Step 3: Write minimal implementation**

```python
# in asr_align.py
if config.should_use_real("asr_align") and _asr_runtime_ready():
    return _run_real_asr(...)
return _run_fake_asr(...)
```

- 增加可观测字段：`execution_mode`, `warnings`。
- 保持既有 `segments_path` 与 `segments` 契约不变。

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_asr_align_adapter.py tests/unit/test_asr_align_real_adapter.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker/worker/adapters/asr_align.py apps/worker/worker/config.py tests/unit/test_asr_align_adapter.py tests/unit/test_asr_align_real_adapter.py
git commit -m "feat(worker): add real asr adapter with safe fake fallback"
```

### Task 3 (T3): Speaker Role 真实适配接入（可回退）

**Files:**
- Modify: `apps/worker/worker/adapters/speaker_role.py`
- Modify: `tests/unit/test_speaker_role_adapter.py`
- Create: `tests/unit/test_speaker_role_real_adapter.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_speaker_role_real_adapter.py
def test_speaker_role_real_mode_emits_speakers_and_segments(monkeypatch, tmp_path):
    ...
    assert result["execution_mode"] == "real"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_speaker_role_real_adapter.py -v`
Expected: FAIL because only fake path exists.

**Step 3: Write minimal implementation**

```python
# in speaker_role.py
if config.should_use_real("speaker_role") and _diarization_runtime_ready():
    artifacts = _run_real_diarization(...)
else:
    artifacts = _run_fake_diarization(...)
```

- 输出维持 `speaker_segments_path`、`speakers_path` 契约。
- 失败时不抛死，记录 `warnings` 并回退 fake。

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_speaker_role_adapter.py tests/unit/test_speaker_role_real_adapter.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker/worker/adapters/speaker_role.py tests/unit/test_speaker_role_adapter.py tests/unit/test_speaker_role_real_adapter.py
git commit -m "feat(worker): add real speaker role adapter with fallback"
```

### Task 4 (T4): QA 指标产物驱动化

**Files:**
- Modify: `apps/worker/worker/adapters/qa_review.py`
- Modify: `apps/worker/worker/pipelines/episode_pipeline_runner.py`
- Modify: `tests/unit/test_qa_review_adapter.py`
- Create: `tests/unit/test_qa_review_metrics_contract.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_qa_review_metrics_contract.py
def test_qa_review_returns_metrics_with_inputs_and_threshold_flags(tmp_path):
    ...
    assert "threshold_flags" in summary
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q tests/unit/test_qa_review_metrics_contract.py -v`
Expected: FAIL because current summary is fixed constants.

**Step 3: Write minimal implementation**

```python
# in qa_review.py
qa_summary = {
    "timing_fit_score": timing_fit_score,
    "voice_stability_score": voice_stability_score,
    "mix_balance_score": mix_balance_score,
    "threshold_flags": threshold_flags,
}
```

- 基于输入产物或阶段结果计算可解释分值。
- 输出保持原 3 分数字段兼容，新增字段追加。

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q tests/unit/test_qa_review_adapter.py tests/unit/test_qa_review_metrics_contract.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/worker/worker/adapters/qa_review.py apps/worker/worker/pipelines/episode_pipeline_runner.py tests/unit/test_qa_review_adapter.py tests/unit/test_qa_review_metrics_contract.py
git commit -m "feat(worker): compute qa summary from run artifacts"
```

### Task 5 (T5): Backend 运行态诊断字段扩展

**Files:**
- Modify: `apps/backend/app/api/routes/pipeline.py`
- Modify: `apps/backend/app/domain/pipeline_run.py`
- Modify: `apps/backend/app/repositories/pipeline_run_store.py`
- Modify: `apps/backend/tests/api/test_pipeline_run_status_api.py`
- Modify: `apps/backend/tests/api/test_pipeline_cost_api.py`

**Step 1: Write the failing test**

```python
# in test_pipeline_run_status_api.py
assert "qa_summary" in status_payload
assert "warnings" in status_payload
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest -q apps/backend/tests/api/test_pipeline_run_status_api.py -v`
Expected: FAIL due to missing keys.

**Step 3: Write minimal implementation**

```python
# in _serialize_run
"qa_summary": run.qa_summary,
"warnings": run.warnings,
```

- 将 worker 返回的 `qa_summary` 与阶段 `warnings` 入库并回传。
- 保持原有字段不删除。

**Step 4: Run test to verify it passes**

Run: `python -m pytest -q apps/backend/tests/api/test_pipeline_run_status_api.py apps/backend/tests/api/test_pipeline_cost_api.py`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/backend/app/api/routes/pipeline.py apps/backend/app/domain/pipeline_run.py apps/backend/app/repositories/pipeline_run_store.py apps/backend/tests/api/test_pipeline_run_status_api.py apps/backend/tests/api/test_pipeline_cost_api.py
git commit -m "feat(backend): expose qa summary and pipeline warnings in run status"
```

### Task 6 (T6): Web 诊断信息可视化（QA + 告警 + 成本）

**Files:**
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/lib/api.ts`
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/tests/smoke/test_runs_pages_contract.js`
- Modify: `apps/web/tests/smoke/test_run_stage_focus_contract.js`

**Step 1: Write the failing test**

```js
if (!detail.includes("质量评分")) process.exit(1);
if (!detail.includes("阶段告警")) process.exit(1);
if (!detail.includes("成本摘要")) process.exit(1);
```

**Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test:e2e`
Expected: FAIL on new contract checks.

**Step 3: Write minimal implementation**

```tsx
<section aria-label="质量评分">...</section>
<section aria-label="阶段告警">...</section>
<section aria-label="成本摘要">...</section>
```

- 仅在数据存在时渲染，避免空噪音。
- 保持现有重跑交互路径不变。

**Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test:e2e`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/web/app/runs/[runId]/page.tsx apps/web/lib/api.ts apps/web/app/globals.css apps/web/tests/smoke/test_runs_pages_contract.js apps/web/tests/smoke/test_run_stage_focus_contract.js
git commit -m "feat(web): visualize qa summary warnings and cost diagnostics"
```

### Task 7 (T7): Playwright 主流程交互回归

**Files:**
- Create: `apps/web/playwright.config.ts`
- Create: `apps/web/tests/e2e/run-flow.spec.ts`
- Modify: `apps/web/package.json`
- Create: `apps/web/tests/e2e/fixtures/mock-backend.ts`

**Step 1: Write the failing test**

```ts
// tests/e2e/run-flow.spec.ts
test('create -> detail -> retry flow', async ({ page }) => {
  await page.goto('/');
  ...
  await expect(page.getByText('任务详情')).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `npm --prefix apps/web run test:playwright`
Expected: FAIL because Playwright setup absent.

**Step 3: Write minimal implementation**

```json
// package.json
"test:playwright": "playwright test"
```

- 搭建 mock backend 响应，覆盖创建、跳转、轮询、失败重跑。
- 首批只做 chromium，后续再扩浏览器矩阵。

**Step 4: Run test to verify it passes**

Run: `npm --prefix apps/web run test:playwright`
Expected: PASS at least one green e2e spec.

**Step 5: Commit**

```bash
git add apps/web/playwright.config.ts apps/web/tests/e2e/run-flow.spec.ts apps/web/tests/e2e/fixtures/mock-backend.ts apps/web/package.json
git commit -m "test(web): add playwright e2e for run create detail retry flow"
```

### Task 8 (T8): 长流程验收与文档收口

**Files:**
- Modify: `README.md`
- Create: `docs/plans/2026-04-19-director-console-phase3-verification.md`
- Modify: `docs/plans/2026-04-19-director-console-phase3-executable-checklist.md`

**Step 1: Run full verification**

Run:

```bash
python -m pytest -q apps/backend/tests
PYTHONPATH=apps/worker python -m pytest -q tests/unit
npm --prefix apps/web run test:e2e
npm --prefix apps/web run test:playwright
```

Expected: all pass.

**Step 2: Manual walkthrough**

- 真实/半真实模式跑一条 episode。
- 记录失败重跑链路是否可恢复。
- 记录 QA 分值和 warnings 是否可读。

**Step 3: Write verification doc**

- 记录命令、输出、通过状态。
- 记录环境依赖：ffmpeg、模型、API key。
- 记录残留风险与下一轮建议。

**Step 4: Update README**

- 增加 `test:playwright`。
- 增加 Phase 3 新字段与诊断说明。

**Step 5: Commit**

```bash
git add README.md docs/plans/2026-04-19-director-console-phase3-verification.md docs/plans/2026-04-19-director-console-phase3-executable-checklist.md
git commit -m "docs: add phase3 verification and rollout notes"
```

## 3. 验收门禁（Phase 3 Done Definition）

- 至少 2 个真实适配器（TTS + ASR 或 Speaker）在 `hybrid/real` 可运行。
- 所有真实适配器失败时可降级 fake，且 run 状态/告警可追踪。
- `GET /api/v1/pipeline-runs/{run_id}` 返回 `qa_summary` + `warnings`。
- 前端详情页可展示质量分、告警、成本摘要。
- Playwright 主流程用例稳定通过（连续 3 次）。

## 4. 残留风险（提前告知）

- 真实供应商 SLA 不稳定时，e2e 不能依赖在线服务，必须 mock。
- 本地重模型依赖安装成本较高，建议优先在 `hybrid` 模式验证链路。
- QA 指标阈值后续仍需样片校准，当前仅提供第一版工程化度量。

## 5. 执行结果（2026-04-19）

- T1 完成：`b66ba48` + `3e25c36` + `784bb55` + `c70b512`
- T2 完成：`37d7491` + `544b8b0`
- T3 完成：`405e2c9` + `c71cacc`
- T4 完成：`c686a59` + `c76bb41`
- T5 完成：`7bae45d` + `ef2e6a6`
- T6 完成：`410a201` + `9629748`
- T7 完成：`d2684d2`
- T8 完成：见 `docs/plans/2026-04-19-director-console-phase3-verification.md`

全量门禁结果：

- `python3 -m pytest -q apps/backend/tests` -> `20 passed`
- `PYTHONPATH=apps/worker python3 -m pytest -q tests/unit` -> `45 passed`
- `npm --prefix apps/web run test:e2e` -> `all smoke contracts passed`
- `npm --prefix apps/web run test:playwright` -> `1 passed`
