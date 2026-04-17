# anime-with-her

面向外语动漫中配化的 AI 配音导演控制台。

## 项目定位

- 按单集生产、按整季沉淀角色资产
- 角色级分轨与重跑优先，支持失败阶段续跑
- 保留原角色音色与情绪表达，逐步走向可规模化中配生产

核心设计文档：

- `docs/design/2026-04-16-ai-dubbing-director-console-integrated-design-v2-1.md`

## 当前能力（Phase 2 + UI/UX Round 2）

- 后端任务编排
  - `run_id` 创建、状态查询、按集历史查询
  - 支持 `start_stage` 从失败阶段重跑
  - 返回 `cost_summary` 与 `qa_summary`
- Worker 七阶段执行链路
  - `media_ingest` → `audio_separation` → `asr_align` → `speaker_role` → `dub_script` → `tts_synthesis` → `mix_master`
- 前端导演台
  - 首页创建任务后自动跳转详情
  - 历史页支持状态筛选 + `run_id` 搜索
  - 详情页支持阶段摘要、异常聚焦、失败重跑
  - 增加骨架屏、可访问性地标、动效降级与触控区规范

## UI/UX 文档

- 第一轮实施计划：`docs/plans/2026-04-17-director-console-ui-ux-optimization-implementation-plan.md`
- 第二轮实施计划：`docs/plans/2026-04-17-director-console-ui-ux-polish-round2-implementation-plan.md`
- 第二轮验证记录：`docs/plans/2026-04-17-director-console-ui-ux-polish-round2-verification.md`

## 本地启动与测试

```powershell
npm run dev:backend
npm run dev:worker
npm run dev:web
```

```powershell
python -m pytest -q apps/backend/tests
$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit
npm.cmd --prefix apps/web run test:e2e
```

## 关键接口

- `POST /api/v1/episodes/{episode_id}/pipeline/run`
  - 请求体：`source_video`、`root`、可选 `start_stage`
- `GET /api/v1/pipeline-runs/{run_id}`
- `GET /api/v1/episodes/{episode_id}/pipeline-runs`
