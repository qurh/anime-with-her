# Director Console UI/UX Polish Round 2 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** 在不改后端契约的前提下，把导演台前端从“可用”提升到“高可读、可操作、低认知负担”的第二轮体验水位。  
**Architecture:** 采用“文案编码与术语先收口 -> 交互与信息架构增强 -> 可访问性与响应式压测收口”的三段式推进。先修正文本与契约，再做页面级功能优化，最后统一验证与文档更新。  
**Tech Stack:** Next.js App Router, React 19, TypeScript, 全局 CSS 设计 token, Node smoke contracts.

---

### Task 1: 文案编码与术语基线收口

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/runs/page.tsx`
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/lib/api.ts`
- Modify: `apps/web/app/api/pipeline/run/route.ts`
- Modify: `apps/web/app/api/pipeline/runs/[runId]/route.ts`
- Create: `apps/web/tests/smoke/test_copy_encoding_contract.js`
- Modify: `apps/web/package.json`

**Step 1: Write the failing test**
```js
// apps/web/tests/smoke/test_copy_encoding_contract.js
const fs = require("fs");
const content = fs.readFileSync("app/runs/[runId]/page.tsx", "utf8");
if (!content.includes("任务详情")) process.exit(1);
if (content.includes("浠诲姟")) process.exit(1); // 禁止常见乱码片段
```

**Step 2: Run test to verify it fails**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL at `test_copy_encoding_contract.js`.

**Step 3: Write minimal implementation**
- 将页面和 API 文案统一为 UTF-8 正常中文。
- 统一术语：`任务`、`任务历史`、`任务详情`、`失败原因`、`重跑起点`。

**Step 4: Run test to verify it passes**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web copy encoding contract ok`.

**Step 5: Commit**
```bash
git add apps/web/app/page.tsx apps/web/app/runs/page.tsx apps/web/app/runs/[runId]/page.tsx apps/web/lib/api.ts apps/web/app/api/pipeline/run/route.ts apps/web/app/api/pipeline/runs/[runId]/route.ts apps/web/tests/smoke/test_copy_encoding_contract.js apps/web/package.json
git commit -m "fix(web): normalize utf8 chinese copy and terminology"
```

---

### Task 2: 历史页可操作性增强（筛选 + 快速定位）

**Files:**
- Modify: `apps/web/app/runs/page.tsx`
- Modify: `apps/web/app/globals.css`
- Create: `apps/web/tests/smoke/test_runs_filter_contract.js`
- Modify: `apps/web/package.json`

**Step 1: Write the failing test**
```js
// 断言存在状态筛选入口与关键词搜索入口
if (!runsPage.includes("状态筛选")) process.exit(1);
if (!runsPage.includes("搜索任务")) process.exit(1);
```

**Step 2: Run test to verify it fails**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL for missing filter/search UI.

**Step 3: Write minimal implementation**
- 历史页增加状态筛选（全部/等待中/运行中/已完成/失败）。
- 增加 run_id 关键词搜索输入框。
- 保持 SSR 初始渲染，筛选在客户端完成。

**Step 4: Run test to verify it passes**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web runs filter contract ok`.

**Step 5: Commit**
```bash
git add apps/web/app/runs/page.tsx apps/web/app/globals.css apps/web/tests/smoke/test_runs_filter_contract.js apps/web/package.json
git commit -m "feat(web): add runs state filter and quick search"
```

---

### Task 3: 任务详情页阶段信息压缩与聚焦

**Files:**
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/app/globals.css`
- Create: `apps/web/tests/smoke/test_run_stage_focus_contract.js`
- Modify: `apps/web/package.json`

**Step 1: Write the failing test**
```js
if (!detail.includes("仅看异常阶段")) process.exit(1);
if (!detail.includes("阶段摘要")) process.exit(1);
```

**Step 2: Run test to verify it fails**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL for missing stage focus controls.

**Step 3: Write minimal implementation**
- 详情页新增“仅看异常阶段”切换。
- 新增阶段摘要（总阶段数/成功/失败/待执行）。
- 保留原有阶段列表，不破坏 `start_stage` 重跑路径。

**Step 4: Run test to verify it passes**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web run stage focus contract ok`.

**Step 5: Commit**
```bash
git add apps/web/app/runs/[runId]/page.tsx apps/web/app/globals.css apps/web/tests/smoke/test_run_stage_focus_contract.js apps/web/package.json
git commit -m "feat(web): improve run detail stage focus and summary"
```

---

### Task 4: 首页交互反馈增强（创建前后状态更明确）

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/globals.css`
- Create: `apps/web/tests/smoke/test_home_feedback_contract.js`
- Modify: `apps/web/package.json`

**Step 1: Write the failing test**
```js
if (!home.includes("预计处理时长")) process.exit(1);
if (!home.includes("创建后将自动跳转")) process.exit(1);
```

**Step 2: Run test to verify it fails**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL on missing UX guidance copy.

**Step 3: Write minimal implementation**
- 首页创建区补充“创建后将自动跳转详情”提示。
- 增加静态引导提示（预计处理时长和路径规范提示）。
- 保持按钮禁用与 loading 状态行为不变。

**Step 4: Run test to verify it passes**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web home feedback contract ok`.

**Step 5: Commit**
```bash
git add apps/web/app/page.tsx apps/web/app/globals.css apps/web/tests/smoke/test_home_feedback_contract.js apps/web/package.json
git commit -m "feat(web): strengthen homepage guidance and interaction feedback"
```

---

### Task 5: 可访问性深度收口（地标、跳转、键盘路径）

**Files:**
- Modify: `apps/web/app/layout.tsx`
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/runs/page.tsx`
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Create: `apps/web/tests/smoke/test_a11y_landmark_contract.js`
- Modify: `apps/web/package.json`

**Step 1: Write the failing test**
```js
if (!layout.includes("跳到主内容")) process.exit(1);
if (!layout.includes("<main")) process.exit(1);
```

**Step 2: Run test to verify it fails**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL for missing skip link / landmark contract.

**Step 3: Write minimal implementation**
- 在布局增加 `Skip to content`（中文文案）跳转链接。
- 页面主内容容器统一加 `id="main-content"`。
- 确认关键按钮文案可读、无纯图标按钮。

**Step 4: Run test to verify it passes**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web a11y landmark contract ok`.

**Step 5: Commit**
```bash
git add apps/web/app/layout.tsx apps/web/app/page.tsx apps/web/app/runs/page.tsx apps/web/app/runs/[runId]/page.tsx apps/web/tests/smoke/test_a11y_landmark_contract.js apps/web/package.json
git commit -m "feat(web): add accessibility landmarks and skip navigation"
```

---

### Task 6: 响应式与动效微调（Interaction Design）

**Files:**
- Modify: `apps/web/app/globals.css`
- Create: `apps/web/tests/smoke/test_interaction_motion_contract.js`
- Modify: `apps/web/package.json`

**Step 1: Write the failing test**
```js
if (!css.includes("transition")) process.exit(1);
if (!css.includes("prefers-reduced-motion")) process.exit(1);
if (!css.includes("min-height: 44px")) process.exit(1);
```

**Step 2: Run test to verify it fails**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL if interaction contract missing.

**Step 3: Write minimal implementation**
- 统一关键交互动画时长到 `120-240ms` 区间。
- 保留 `prefers-reduced-motion` 降级策略。
- 保障移动端可点击区域（>=44px）。

**Step 4: Run test to verify it passes**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web interaction motion contract ok`.

**Step 5: Commit**
```bash
git add apps/web/app/globals.css apps/web/tests/smoke/test_interaction_motion_contract.js apps/web/package.json
git commit -m "feat(web): refine interaction motion and touch ergonomics"
```

---

### Task 7: 统一页面骨架与无布局跳动加载态

**Files:**
- Create: `apps/web/app/components/LoadingSkeleton.tsx`
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/app/globals.css`
- Create: `apps/web/tests/smoke/test_skeleton_contract.js`
- Modify: `apps/web/package.json`

**Step 1: Write the failing test**
```js
if (!detail.includes("LoadingSkeleton")) process.exit(1);
if (!css.includes(".skeleton")) process.exit(1);
```

**Step 2: Run test to verify it fails**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: FAIL for missing skeleton implementation.

**Step 3: Write minimal implementation**
- 新增可复用 `LoadingSkeleton` 组件。
- 详情页初次加载使用骨架占位，减少布局跳动。
- 不改变现有轮询逻辑。

**Step 4: Run test to verify it passes**
Run: `npm.cmd --prefix apps/web run test:e2e`  
Expected: PASS with `web skeleton contract ok`.

**Step 5: Commit**
```bash
git add apps/web/app/components/LoadingSkeleton.tsx apps/web/app/runs/[runId]/page.tsx apps/web/app/globals.css apps/web/tests/smoke/test_skeleton_contract.js apps/web/package.json
git commit -m "feat(web): add reusable skeleton loading for run detail"
```

---

### Task 8: 验证与文档收口

**Files:**
- Modify: `README.md`
- Create: `docs/plans/2026-04-17-director-console-ui-ux-polish-round2-verification.md`

**Step 1: Run full verification**
Run:
```bash
python -m pytest -q apps/backend/tests
$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit
npm.cmd --prefix apps/web run test:e2e
```
Expected: 全部通过。

**Step 2: Manual UX walkthrough**
- 首页：创建任务交互与文案清晰
- 历史页：筛选与快速定位可用
- 详情页：阶段聚焦与重跑路径清晰
- 键盘路径与读屏提示有效

**Step 3: Write verification doc**
- 记录命令、输出、通过状态、残留问题。

**Step 4: Update README**
- 增补“UI/UX Round 2”说明与测试命令。

**Step 5: Commit**
```bash
git add README.md docs/plans/2026-04-17-director-console-ui-ux-polish-round2-verification.md
git commit -m "docs(web): add ui ux round2 verification report"
```

---

## Notes

- 本计划严格基于现有接口，不新增后端 API 依赖。  
- 实施时优先修复文案编码问题，再推进交互增强。  
- 所有新增体验点都必须有对应 smoke 合约，避免回退。

