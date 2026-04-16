# anime-with-her

面向外语动漫中配化的 AI 配音导演控制台。

当前项目以文档驱动推进，设计基线如下：

- `docs/design/2026-04-16-ai-dubbing-director-console-integrated-design-v2-1.md`

核心方向：

- 按单集生产
- 按整季沉淀角色资产
- 表演与情绪复刻优先，音色相似为辅
- 先角色分析确认，再生成整集
- 支持关键片段精修与重生成

## 当前能力（Phase 2）

- 后端任务化串跑：支持 `run_id`、状态查询、按集历史查询
- Worker 7 阶段执行：支持失败落盘、`start_stage` 分阶段重跑
- 成本与 QA：串跑任务包含 `cost_summary` 与 `qa_summary`
- 导演台 Web：
  - 首页创建任务并跳转到详情
  - `/runs?episode_id=<id>` 查看历史任务
  - `/runs/<run_id>` 查看阶段状态、错误信息、最终产物
  - 失败任务支持“从阶段重跑”入口

## 开发命令

```powershell
npm run dev:backend
npm run dev:worker
npm run dev:web
python -m pytest -q apps/backend/tests
$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit
npm.cmd --prefix apps/web run test:e2e
```

## 关键接口

- `POST /api/v1/episodes/{episode_id}/pipeline/run`
  - 请求体：`source_video`、`root`、可选 `start_stage`
- `GET /api/v1/pipeline-runs/{run_id}`
- `GET /api/v1/episodes/{episode_id}/pipeline-runs`
