const fs = require("fs");

const runsPagePath = "app/runs/page.tsx";
if (!fs.existsSync(runsPagePath)) {
  console.error("Missing runs page:", runsPagePath);
  process.exit(1);
}

const runsPage = fs.readFileSync(runsPagePath, "utf8");

if (!runsPage.includes("状态筛选")) {
  console.error("Runs page should include 状态筛选 entry.");
  process.exit(1);
}
if (!runsPage.includes("搜索任务")) {
  console.error("Runs page should include 搜索任务 input.");
  process.exit(1);
}
if (!runsPage.includes("全部") || !runsPage.includes("等待中") || !runsPage.includes("运行中") || !runsPage.includes("已完成") || !runsPage.includes("失败")) {
  console.error("Runs page should include all state filter options.");
  process.exit(1);
}

console.log("web runs filter contract ok");
