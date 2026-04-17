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
if (!runDetailPage.includes("返回任务历史")) {
  console.error("Run detail page should include action: 返回任务历史.");
  process.exit(1);
}

console.log("web runs pages contract ok");
