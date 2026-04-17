# Director Console UI/UX Optimization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task.

**Goal:** 在不破坏现有后端契约与任务流程的前提下，将导演台前端升级为“可读、可控、可恢复、可扩展”的高质量 UI/UX 版本。  
**Architecture:** 采用“设计规范先行 + 页面分层重构 + 可访问性与响应式收口”策略。先固化视觉/交互规范，再逐页迭代首页、任务历史页、任务详情页，最后通过 smoke contract + 手工验收闭环。  
**Tech Stack:** Next.js 15 (App Router), React 19, TypeScript, CSS Modules-free global CSS（当前基线）, Node 脚本 smoke tests.

## 0. 背景与基线结论（来自当前代码分析）

1. 当前三页主流程已可用：创建任务 -> 查看历史 -> 详情重跑。  
2. 存在 UI/UX 关键缺口：
- 文案编码异常（`apps/web/app/runs/[runId]/page.tsx` 与部分 smoke 脚本出现乱码）
- 视觉系统薄弱（缺少统一设计 tokens、状态色、层级规范）
- 信息架构可读性一般（状态、成本、失败原因、重跑入口的优先级还不够清晰）
- 可访问性不足（错误提示未统一 `role="alert"`/`aria-live`，焦点态不完整）
- 响应式与加载反馈需要增强（缺少骨架/占位规范，可能引发布局跳动）

3. 设计方向（基于 `ui-ux-pro-max` 检索）：
- 风格建议：`Swiss Modernism 2.0`（高可读、高性能、低复杂度）
- 字体建议：`Noto Sans SC`（简中一致性与可读性）
- 色彩建议：蓝系主色 + 橙色 CTA（高对比，适合任务控制台）
- UX 必做项：颜色对比、错误可宣读、非颜色单一表达、ARIA 标签

---

## Task 1: 输出 UI/UX 设计规格文档（先设计后实现）

**Files:**
- Create: `docs/design/2026-04-17-director-console-ui-ux-spec-v1.md`
- Modify: `docs/plans/2026-04-17-director-console-ui-ux-optimization-implementation-plan.md`（如设计结论需回写）

**Step 1: 定义信息架构与用户路径**
- 明确 3 条主路径：新建任务、追踪任务、失败恢复。
- 明确每页核心目标与“首屏必须看到的信息”。

**Step 2: 定义视觉系统**
- 规范颜色 token（主色/状态色/背景/边框/文本）。
- 规范字体层级（H1/H2/body/caption）和间距尺度（4/8/12/16/24/32）。

**Step 3: 定义交互规范**
- 表单错误、按钮禁用、加载态、轮询状态提示、重跑确认流程。
- 定义“不可仅靠颜色表达状态”规则（颜色 + 图标/文案）。

**Step 4: 定义可访问性与响应式规范**
- `aria-live`, `role=alert`, 焦点可见性、键盘可达。
- 断点下布局规则（mobile/tablet/desktop）。

**Step 5: Commit**
```bash
git add docs/design/2026-04-17-director-console-ui-ux-spec-v1.md docs/plans/2026-04-17-director-console-ui-ux-optimization-implementation-plan.md
git commit -m "docs(ui): add director console ui ux spec v1"
```

---

## Task 2: 先修复文案编码与术语一致性（高优先级）

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/runs/page.tsx`
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/tests/smoke/test_runs_pages_contract.js`
- Test: `apps/web/tests/smoke/test_existing_pages_contract.js`

**Step 1: 写失败测试（文案契约）**
- 在 `test_runs_pages_contract.js` 中新增关键中文文案断言（任务详情、阶段状态、最终产物等）。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```
预期：在文案断言处 FAIL（乱码或缺失）。

**Step 3: 最小实现修复**
- 修复页面文件中的乱码文案。
- 统一术语：`任务`, `运行`, `阶段状态`, `失败原因`, `重跑`, `最终产物`。

**Step 4: 运行测试确认通过**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/app/page.tsx apps/web/app/runs/page.tsx apps/web/app/runs/[runId]/page.tsx apps/web/tests/smoke/test_runs_pages_contract.js
git commit -m "fix(web): normalize chinese copy and encoding across run pages"
```

---

## Task 3: 建立设计 Tokens 与全局排版体系

**Files:**
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/app/layout.tsx`
- Create: `apps/web/tests/smoke/test_ui_tokens_contract.js`
- Modify: `apps/web/package.json`（将新 smoke 纳入 `test:e2e`）

**Step 1: 写失败测试（token 契约）**
- 新增 `test_ui_tokens_contract.js`：检查 `globals.css` 中存在 `--color-*`, `--space-*`, `--radius-*` 等关键变量。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 3: 最小实现**
- 在 `:root` 中建立 token 变量。
- 引入更一致的字体方案（优先 `Noto Sans SC`，在 `layout.tsx` 统一注入）。
- 统一基础控件样式：输入框、按钮、卡片、焦点态。

**Step 4: 回归测试**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/app/globals.css apps/web/app/layout.tsx apps/web/tests/smoke/test_ui_tokens_contract.js apps/web/package.json
git commit -m "feat(web): add design tokens and typography baseline"
```

---

## Task 4: 首页重构为“任务创建控制台”

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/globals.css`
- Test: `apps/web/tests/smoke/test_existing_pages_contract.js`

**Step 1: 写失败测试（首页结构契约）**
- 断言首页包含：目标说明区、表单区、结果反馈区、任务历史入口。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 3: 最小实现**
- 优化首屏信息层级（标题/副标题/表单动作）。
- 提升表单可用性：字段说明、占位提示、提交态文案。
- 创建成功后保留“去任务历史”快捷路径。

**Step 4: 回归测试**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/app/page.tsx apps/web/app/globals.css apps/web/tests/smoke/test_existing_pages_contract.js
git commit -m "feat(web): redesign homepage task creation experience"
```

---

## Task 5: 任务历史页优化（可扫描、可筛选、可比对）

**Files:**
- Modify: `apps/web/app/runs/page.tsx`
- Modify: `apps/web/app/globals.css`
- Test: `apps/web/tests/smoke/test_runs_pages_contract.js`

**Step 1: 写失败测试（历史页契约）**
- 断言状态 badge、更新时间、失败阶段提示、详情入口同时存在。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 3: 最小实现**
- 增加状态 badge（pending/running/success/failed）。
- 增加空状态与引导行动（返回首页创建任务）。
- 强化 run 卡片信息密度与对齐。

**Step 4: 回归测试**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/app/runs/page.tsx apps/web/app/globals.css apps/web/tests/smoke/test_runs_pages_contract.js
git commit -m "feat(web): improve runs list readability and state visibility"
```

---

## Task 6: 任务详情页优化（状态诊断 + 重跑决策）

**Files:**
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Modify: `apps/web/app/globals.css`
- Test: `apps/web/tests/smoke/test_run_retry_contract.js`

**Step 1: 写失败测试（详情结构契约）**
- 断言详情页包含：总体状态、阶段列表、最终产物、失败原因、重跑表单。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 3: 最小实现**
- 优化阶段状态展示（时间线/分组列表均可，但需可扫读）。
- 突出失败原因卡片与推荐重跑起点（默认失败阶段）。
- 增强轮询反馈（运行中提示 + 上次更新时间）。

**Step 4: 回归测试**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/app/runs/[runId]/page.tsx apps/web/app/globals.css apps/web/tests/smoke/test_run_retry_contract.js
git commit -m "feat(web): enhance run detail diagnostics and retry ux"
```

---

## Task 7: 可访问性（A11y）与错误反馈收口

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Create: `apps/web/tests/smoke/test_accessibility_contract.js`
- Modify: `apps/web/package.json`

**Step 1: 写失败测试（A11y 契约）**
- 断言错误提示区域具备 `role="alert"` 或 `aria-live="polite/assertive"`。
- 断言关键操作按钮有可读 label（避免仅图标语义）。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 3: 最小实现**
- 给错误容器加 `role="alert"`/`aria-live`。
- 为动态状态与重跑控件补充可读文本与 ARIA 属性。
- 补焦点样式（键盘导航可见）。

**Step 4: 回归测试**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/app/page.tsx apps/web/app/runs/[runId]/page.tsx apps/web/tests/smoke/test_accessibility_contract.js apps/web/package.json
git commit -m "feat(web): add accessibility contracts and alert semantics"
```

---

## Task 8: 响应式与动效优化（性能友好）

**Files:**
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/runs/page.tsx`
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Create: `apps/web/tests/smoke/test_responsive_motion_contract.js`
- Modify: `apps/web/package.json`

**Step 1: 写失败测试（响应式/动效契约）**
- 断言存在 `@media (prefers-reduced-motion: reduce)`。
- 断言存在移动端布局规则（如断点下卡片改为单列）。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 3: 最小实现**
- 增加 reduce-motion 降级策略。
- 调整小屏排版与按钮触达尺寸。
- 增加轻量入场动效，不影响可访问性和性能。

**Step 4: 回归测试**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/app/globals.css apps/web/app/page.tsx apps/web/app/runs/page.tsx apps/web/app/runs/[runId]/page.tsx apps/web/tests/smoke/test_responsive_motion_contract.js apps/web/package.json
git commit -m "feat(web): improve responsive layout and motion accessibility"
```

---

## Task 9: 前后端联调文案与状态语义统一

**Files:**
- Modify: `apps/web/lib/api.ts`
- Modify: `apps/web/app/api/pipeline/run/route.ts`
- Modify: `apps/web/app/api/pipeline/runs/[runId]/route.ts`
- Modify: `apps/web/app/runs/[runId]/page.tsx`
- Create: `apps/web/tests/smoke/test_api_error_copy_contract.js`

**Step 1: 写失败测试（错误文案契约）**
- 断言常见错误场景文案统一且可行动（例如：网络失败、后端失败、参数缺失）。

**Step 2: 运行测试确认失败**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 3: 最小实现**
- 统一 API 层错误映射与用户可读文案。
- 区分“可重试错误”与“需人工处理错误”。

**Step 4: 回归测试**
```bash
npm.cmd --prefix apps/web run test:e2e
```

**Step 5: Commit**
```bash
git add apps/web/lib/api.ts apps/web/app/api/pipeline/run/route.ts apps/web/app/api/pipeline/runs/[runId]/route.ts apps/web/app/runs/[runId]/page.tsx apps/web/tests/smoke/test_api_error_copy_contract.js
git commit -m "feat(web): unify api error semantics and user-facing messages"
```

---

## Task 10: 收口验证与文档更新

**Files:**
- Modify: `README.md`
- Create: `docs/plans/2026-04-17-director-console-ui-ux-optimization-verification.md`

**Step 1: 执行完整验证**
```bash
python -m pytest -q apps/backend/tests
$env:PYTHONPATH="apps/worker"; python -m pytest -q tests/unit
npm.cmd --prefix apps/web run test:e2e
```

**Step 2: 手工体验验收（建议录屏）**
- 桌面端：创建任务 -> 跳转详情 -> 状态轮询 -> 失败重跑
- 移动端宽度：首页、历史页、详情页布局可读
- 键盘路径：Tab 顺序、焦点可见、错误可宣读

**Step 3: 写验证文档**
- 记录命令、输出、通过/失败状态
- 记录残留问题与下一轮优化建议

**Step 4: 更新 README UI/UX 小节**
- 增加“导演台交互流程”和“可访问性”说明

**Step 5: Commit**
```bash
git add README.md docs/plans/2026-04-17-director-console-ui-ux-optimization-verification.md
git commit -m "docs(web): add ui ux optimization verification report"
```

---

## 非目标（本轮不做）

1. 新增复杂组件库（如全面迁移 Tailwind/shadcn）  
2. 引入大而全图表系统（仅保留任务看板必要信息）  
3. 视频编辑器级时间轴可视化  
4. 彻底重写现有路由结构

## 里程碑

1. **M1 体验可读性**：乱码清零 + 文案统一 + 视觉 token 落地  
2. **M2 任务可操作性**：历史页与详情页的信息层级优化完成  
3. **M3 体验质量门禁**：A11y、响应式、动效与错误语义通过 smoke 契约  
4. **M4 可交付**：验证文档齐备，可进入下一轮业务能力迭代

