const fs = require("fs");

const files = [
  "app/runs/page.tsx",
  "app/runs/[runId]/page.tsx",
  "app/api/pipeline/runs/[runId]/route.ts",
  "lib/api.ts",
];

for (const filePath of files) {
  if (!fs.existsSync(filePath)) {
    console.error("Missing file:", filePath);
    process.exit(1);
  }
}

const home = fs.readFileSync("app/page.tsx", "utf8");
if (!home.includes("/runs/")) {
  console.error("Homepage should include navigation to run detail page.");
  process.exit(1);
}

const runsPage = fs.readFileSync("app/runs/page.tsx", "utf8");
if (!runsPage.includes("任务历史")) {
  console.error("Runs page should include task history heading.");
  process.exit(1);
}
if (!runsPage.includes("status-badge")) {
  console.error("Runs page should render status-badge for readability.");
  process.exit(1);
}
if (!runsPage.includes("暂无运行记录")) {
  console.error("Runs page should include empty-state guidance.");
  process.exit(1);
}

const runDetailPage = fs.readFileSync("app/runs/[runId]/page.tsx", "utf8");
if (!runDetailPage.includes("阶段状态")) {
  console.error("Run detail page should include stage status section.");
  process.exit(1);
}
if (!runDetailPage.includes("最终产物")) {
  console.error("Run detail page should include final outputs section.");
  process.exit(1);
}
if (!runDetailPage.includes("任务详情")) {
  console.error("Run detail page should include Chinese heading: 任务详情.");
  process.exit(1);
}
if (!runDetailPage.includes("任务 ID")) {
  console.error("Run detail page should include Chinese label: 任务 ID.");
  process.exit(1);
}
if (runDetailPage.includes("Run ID")) {
  console.error("Run detail page should not expose mixed English label: Run ID.");
  process.exit(1);
}
if (!runDetailPage.includes("失败原因")) {
  console.error("Run detail page should include Chinese label: 失败原因.");
  process.exit(1);
}
if (!runDetailPage.includes("质量评分")) {
  console.error("Run detail page should include diagnostics section: 质量评分.");
  process.exit(1);
}
if (!runDetailPage.includes("阶段告警")) {
  console.error("Run detail page should include diagnostics section: 阶段告警.");
  process.exit(1);
}
if (!runDetailPage.includes("成本摘要")) {
  console.error("Run detail page should include diagnostics section: 成本摘要.");
  process.exit(1);
}
if (!runDetailPage.includes("const hasQaDiagnostics")) {
  console.error("Run detail page should define hasQaDiagnostics for conditional diagnostics rendering.");
  process.exit(1);
}
if (!runDetailPage.includes("const hasStageWarnings")) {
  console.error("Run detail page should define hasStageWarnings for conditional diagnostics rendering.");
  process.exit(1);
}
if (!runDetailPage.includes("const hasCostSummary")) {
  console.error("Run detail page should define hasCostSummary for conditional diagnostics rendering.");
  process.exit(1);
}
if (!runDetailPage.includes("{hasQaDiagnostics ? (")) {
  console.error("Run detail page should gate 质量评分 section behind hasQaDiagnostics.");
  process.exit(1);
}
if (!runDetailPage.includes("{hasStageWarnings ? (")) {
  console.error("Run detail page should gate 阶段告警 section behind hasStageWarnings.");
  process.exit(1);
}
if (!runDetailPage.includes("{hasCostSummary ? (")) {
  console.error("Run detail page should gate 成本摘要 section behind hasCostSummary.");
  process.exit(1);
}
if (!runDetailPage.includes('typeof flag.is_below_threshold === "boolean"')) {
  console.error("Run detail page should guard threshold flag shape: is_below_threshold boolean.");
  process.exit(1);
}
if (!runDetailPage.includes('typeof flag.reason === "string"')) {
  console.error("Run detail page should guard threshold flag shape: reason string.");
  process.exit(1);
}
if (!runDetailPage.includes("返回任务历史")) {
  console.error("Run detail page should include action: 返回任务历史.");
  process.exit(1);
}

console.log("web runs pages contract ok");
