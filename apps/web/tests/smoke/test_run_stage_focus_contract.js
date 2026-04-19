const fs = require("fs");

const detailPath = "app/runs/[runId]/page.tsx";
if (!fs.existsSync(detailPath)) {
  console.error("Missing run detail page:", detailPath);
  process.exit(1);
}

const detail = fs.readFileSync(detailPath, "utf8");

if (!detail.includes("仅看异常阶段")) {
  console.error("Run detail page should include 仅看异常阶段 toggle.");
  process.exit(1);
}

if (!detail.includes("阶段摘要")) {
  console.error("Run detail page should include 阶段摘要.");
  process.exit(1);
}

if (!detail.includes("阶段告警")) {
  console.error("Run detail page should include 阶段告警 section.");
  process.exit(1);
}

if (!detail.includes("质量评分")) {
  console.error("Run detail page should include 质量评分 section.");
  process.exit(1);
}

if (!detail.includes("const hasQaDiagnostics")) {
  console.error("Run detail page should define hasQaDiagnostics gate.");
  process.exit(1);
}

if (!detail.includes("const hasStageWarnings")) {
  console.error("Run detail page should define hasStageWarnings gate.");
  process.exit(1);
}

if (!detail.includes("const hasCostSummary")) {
  console.error("Run detail page should define hasCostSummary gate.");
  process.exit(1);
}

if (!/\{hasQaDiagnostics \?\s*\(\s*<section className="panel">\s*<h2>质量评分<\/h2>/s.test(detail)) {
  console.error("Run detail page should conditionally render 质量评分 via hasQaDiagnostics.");
  process.exit(1);
}

if (!/\{hasStageWarnings \?\s*\(\s*<section className="panel">\s*<h2>阶段告警<\/h2>/s.test(detail)) {
  console.error("Run detail page should conditionally render 阶段告警 via hasStageWarnings.");
  process.exit(1);
}

if (!/\{hasCostSummary \?\s*\(\s*<section className="panel">\s*<h2>成本摘要<\/h2>/s.test(detail)) {
  console.error("Run detail page should conditionally render 成本摘要 via hasCostSummary.");
  process.exit(1);
}

console.log("web run stage focus contract ok");
