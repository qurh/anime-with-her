# AI Dubbing Director Console Phase 2 Implementation Plan

> **For Claude/Codex:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

## 1. 文档信息

- 日期：2026-04-16
- 版本：v1
- 目标阶段：从“契约级端到端骨架”升级到“可持续迭代的工程化执行链路”
- 设计基线：`docs/design/2026-04-16-ai-dubbing-director-console-integrated-design-v2-1.md`
- 上一阶段计划：`docs/plans/2026-04-16-ai-dubbing-director-console-implementation-plan.md`

## 2. 当前基线（已完成）

当前仓库已具备以下基础能力：

1. `apps/backend`：核心领域模型 + 主要 API + 一键整集串跑触发接口。
2. `apps/worker`：7 阶段适配器契约（ingest/separation/asr/speaker/dub_script/tts/mix）+ `episode_pipeline_runner`。
3. `apps/web`：可触发整集串跑并展示阶段状态和输出路径。
4. 全量自动化验证通过：
   - `python -m pytest -q apps/backend/tests`
   - `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit`
   - `npm.cmd --prefix apps/web run test:e2e`

## 3. Phase 2 总体目标

在不破坏现有契约和测试稳定性的前提下，完成以下三件事：

1. 把“整集串跑”从同步调用升级为可追踪、可恢复、可观测的任务模型。
2. 把关键适配器从纯占位实现升级为“真适配能力 + 可降级 fake”双模式。
3. 把导演台从“可触发”升级为“可跟踪任务、可定位失败、可查看产物”。

## 4. 执行规则

1. 每个任务必须先写失败测试，再写最小实现，再回归通过。
2. 每个任务完成后提交一次 commit，保持可回滚。
3. 真实能力接入必须保持原有输出契约不变（向后兼容）。
4. 所有外部依赖（FFmpeg/模型/API）必须通过适配层注入，不可直接散落在业务代码中。
5. 完成宣称前必须执行：
   - `python -m pytest -q apps/backend/tests`
   - `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit`
   - `npm.cmd --prefix apps/web run test:e2e`

## 5. 实施阶段与任务

## Phase 2.1：任务化编排与可追踪运行

### Task 1：引入 Pipeline Run 数据模型与存储

**目标：** 让一次整集串跑具备独立 `run_id`、状态机和阶段状态记录。

**Files:**
- Create: `apps/backend/app/domain/pipeline_run.py`
- Create: `apps/backend/app/repositories/pipeline_run_store.py`
- Create: `apps/backend/tests/unit/test_pipeline_run_store.py`

**验收标准：**
- 可创建 `run_id`，状态从 `pending -> running -> success/failed`。
- 支持按 `episode_id` 查询最近运行记录。

### Task 2：后端 API 改为“触发 + 查询”双接口

**目标：** 将当前同步返回改造为任务化返回，便于前端轮询和失败诊断。

**Files:**
- Modify: `apps/backend/app/api/routes/pipeline.py`
- Modify: `apps/backend/app/main.py`
- Create: `apps/backend/tests/api/test_pipeline_run_status_api.py`

**API 目标：**
- `POST /api/v1/episodes/{episode_id}/pipeline/run`：返回 `run_id` 和初始状态。
- `GET /api/v1/pipeline-runs/{run_id}`：返回整体状态、阶段状态、输出和错误。
- `GET /api/v1/episodes/{episode_id}/pipeline-runs`：返回历史运行列表。

**验收标准：**
- 前端可通过 `run_id` 获取完整进度信息。
- 兼容当前阶段结果结构（不破坏旧字段语义）。

## Phase 2.2：Worker Runner 稳健性

### Task 3：Runner 阶段化错误捕获与失败落盘

**目标：** 某阶段异常时能明确记录失败阶段、错误摘要、可重试输入。

**Files:**
- Modify: `apps/worker/worker/pipelines/episode_pipeline_runner.py`
- Create: `tests/unit/test_episode_pipeline_runner_failures.py`

**验收标准：**
- 失败时返回 `state=failed`、`failed_stage`、`error`。
- 成功阶段结果仍可保留（便于后续重跑）。

### Task 4：Runner 支持从指定阶段重跑

**目标：** 降低整集重跑成本，支持从失败阶段或人工指定阶段恢复。

**Files:**
- Modify: `apps/worker/worker/pipelines/episode_pipeline_runner.py`
- Create: `tests/unit/test_episode_pipeline_runner_resume.py`

**验收标准：**
- `start_stage` 参数可用。
- 在已有产物存在时可跳过前序阶段并继续执行。

## Phase 2.3：真实能力接入（保留 fake 回退）

### Task 5：统一适配器配置层（real/fake/provider）

**目标：** 用统一配置控制每个阶段使用 fake 还是 real 实现。

**Files:**
- Create: `apps/worker/worker/config.py`
- Modify: `apps/worker/worker/adapters/*.py`（按需）
- Create: `tests/unit/test_worker_config.py`

**验收标准：**
- 支持环境变量控制：`WORKER_MODE=fake|hybrid|real`。
- `hybrid` 下允许单阶段 real、其他阶段 fake。

### Task 6：Media Ingest 真实 FFmpeg 适配

**目标：** 首个真实能力落地：视频标准化与音频提取。

**Files:**
- Modify: `apps/worker/worker/adapters/media_ingest.py`
- Create: `tests/unit/test_media_ingest_real_adapter.py`
- Create: `scripts/check-ffmpeg.ps1`

**验收标准：**
- 当 FFmpeg 可用时执行真实命令；不可用时回退 fake 并给出清晰告警。
- 输出契约保持不变（`source_video_path`、`normalized_vocals_path`）。

### Task 7：TTS 供应商真实调用封装（带降级）

**目标：** 保持现有主备路由结构，增加真实 API 客户端壳层。

**Files:**
- Modify: `apps/worker/worker/adapters/tts_provider.py`
- Modify: `apps/worker/worker/adapters/tts_synthesis.py`
- Create: `tests/unit/test_tts_provider_live_contract.py`

**验收标准：**
- 无密钥时默认 fake，不阻塞本地开发。
- 有密钥时可调用真实 API，失败时自动降级到 fallback。

## Phase 2.4：预算与质量控制前置

### Task 8：将预算估算与串跑任务绑定

**目标：** 在触发串跑前给出成本估算，运行中记录实际消耗。

**Files:**
- Create: `apps/backend/app/services/cost_estimator.py`
- Modify: `apps/backend/app/api/routes/pipeline.py`
- Create: `apps/backend/tests/api/test_pipeline_cost_api.py`

**验收标准：**
- 返回 `estimated_cost`、`estimated_duration`。
- 任务结果中附带 `cost_summary`。

### Task 9：基础 QA 评估汇总

**目标：** 在 `mix_master` 后输出基础 QA 指标（占位 + 可扩展）。

**Files:**
- Create: `apps/worker/worker/adapters/qa_review.py`
- Modify: `apps/worker/worker/pipelines/episode_pipeline_runner.py`
- Create: `tests/unit/test_qa_review_adapter.py`

**验收标准：**
- runner 返回 `qa_summary` 字段。
- 包含至少：`timing_fit_score`、`voice_stability_score`、`mix_balance_score`。

## Phase 2.5：导演台任务看板化

### Task 10：前端任务列表与详情页

**目标：** 除了触发串跑，还能查看历史任务与当前任务详情。

**Files:**
- Create: `apps/web/app/runs/page.tsx`
- Create: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/app/page.tsx`
- Create: `apps/web/lib/api.ts`
- Create: `apps/web/app/api/pipeline/runs/[runId]/route.ts`

**验收标准：**
- 首页触发后可跳转任务详情。
- 任务详情可展示阶段状态、失败信息、最终输出路径。

### Task 11：前端失败提示与重跑入口

**目标：** 当任务失败时，给出可操作的“从阶段重跑”入口。

**Files:**
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/app/api/pipeline/run/route.ts`
- Create: `apps/web/tests/smoke/test_run_retry_contract.js`（或沿用现有脚本模式）

**验收标准：**
- 能提交 `start_stage` 触发重跑。
- UI 能清晰区分“新任务触发”和“失败任务恢复”。

## 6. 最终验证门禁

### Task 12：Phase 2 收口验证与文档更新

**Files:**
- Modify: `README.md`
- Create: `docs/plans/2026-04-16-ai-dubbing-director-console-phase2-verification.md`

**必须执行：**
- `python -m pytest -q apps/backend/tests`
- `$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit`
- `npm.cmd --prefix apps/web run test:e2e`

**文档要求：**
- 记录命令、关键输出、是否通过。
- 记录真实依赖准备情况（FFmpeg、供应商密钥、模型目录）。

## 7. 非目标（本期不做）

1. 全量多机分布式调度。
2. 影视级口型同步精修引擎。
3. 复杂 DAW 式时间轴编辑器。
4. 所有阶段一次性全部切换为真实模型。

## 8. 里程碑定义

1. **M1（任务化）**：后端 `run_id` 模型 + 查询 API + 前端可追踪。
2. **M2（稳健性）**：runner 失败可定位、支持分阶段恢复。
3. **M3（真实能力起步）**：至少一个真实适配器上线且可降级。
4. **M4（运营闭环）**：预算与 QA 指标可见，任务看板可用。
