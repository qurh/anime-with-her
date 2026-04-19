# 2026-04-19 Director Console Phase 3 Verification

## 执行环境

- 目录：`/Users/qrh/projects/anime-with-her/.worktrees/phase3-exec`
- 分支：`feat/phase3-exec`
- 日期：`2026-04-19`

## 验证命令与结果

1. 后端 API 测试

```bash
python3 -m pytest -q apps/backend/tests
```

结果：`20 passed in 0.05s`

2. Worker 单元测试

```bash
PYTHONPATH=apps/worker python3 -m pytest -q tests/unit
```

结果：`45 passed in 0.05s`

3. Web smoke 契约测试

```bash
npm --prefix apps/web run test:e2e
```

结果：全部通过（包含 runs/detail/retry、token、a11y、responsive、skeleton 等合约）

4. Web Playwright 主流程回归

```bash
npm --prefix apps/web run test:playwright
```

结果：`1 passed (create -> detail -> retry flow)`

## 半真实链路演练（hybrid）

执行命令：

```bash
PYTHONPATH=apps/worker WORKER_MODE=hybrid WORKER_REAL_STAGES=asr_align,speaker_role python3 - <<'PY'
from worker.pipelines.episode_pipeline_runner import run_episode_pipeline
result = run_episode_pipeline(episode_id='episode_phase3_manual', source_video='data/input/demo.mkv', root='data/episodes')
print('state:', result['state'])
print('failed_stage:', result.get('failed_stage'))
print('qa_summary_keys:', sorted(result.get('qa_summary', {}).keys()))
print('asr_mode:', result['stage_results']['asr_align'].get('execution_mode'))
print('asr_warnings:', result['stage_results']['asr_align'].get('warnings'))
print('speaker_mode:', result['stage_results']['speaker_role'].get('execution_mode'))
print('speaker_warnings:', result['stage_results']['speaker_role'].get('warnings'))
PY
```

关键结果：

- `state: success`
- `qa_summary_keys` 包含：`timing_fit_score`、`voice_stability_score`、`mix_balance_score`、`threshold_flags`
- `asr_align` 与 `speaker_role` 在本机 runtime 不可用时按预期降级到 `fake`
- warning 可追踪：`asr runtime unavailable...` / `speaker role runtime unavailable...`

## 依赖准备情况

- `ffmpeg`：`missing`
- `ALIYUN_TTS_API_KEY`：`missing`
- `DOUBAO_TTS_API_KEY`：`missing`
- `models/`：`missing`

## 结论

- Phase 3 任务 1-8 已完成并通过当前门禁。
- 系统具备以下新增能力：
  - TTS / ASR / Speaker 真实适配器接入框架 + 失败回退
  - QA 指标产物驱动化 + 阈值标记
  - 后端状态接口返回 `qa_summary` 与 `warnings`
  - 前端详情页诊断区（质量评分 / 阶段告警 / 成本摘要）
  - Playwright 主流程回归（创建 -> 详情 -> 重跑）

## 残留风险与下一步建议

- Playwright 目前覆盖单条主路径，建议扩展到网络错误、空诊断数据、失败重跑失败等场景。
- 真实供应商能力仍依赖本机 runtime 与密钥，当前默认以 fake/hybrid 验证链路稳定性。
- QA 指标目前为工程化可解释分值，后续需结合样片反馈继续校准阈值。
