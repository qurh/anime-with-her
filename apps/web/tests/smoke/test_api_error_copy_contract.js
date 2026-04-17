const fs = require("fs");

const files = [
  "lib/api.ts",
  "app/api/pipeline/run/route.ts",
  "app/api/pipeline/runs/[runId]/route.ts",
];

for (const filePath of files) {
  if (!fs.existsSync(filePath)) {
    console.error("Missing file:", filePath);
    process.exit(1);
  }
}

const api = fs.readFileSync("lib/api.ts", "utf8");
const runRoute = fs.readFileSync("app/api/pipeline/run/route.ts", "utf8");
const runsRoute = fs.readFileSync("app/api/pipeline/runs/[runId]/route.ts", "utf8");

if (!api.includes("后端请求失败")) {
  console.error("lib/api.ts should include normalized error text: 后端请求失败。");
  process.exit(1);
}
if (!runRoute.includes("episode_id 和 source_video 为必填项")) {
  console.error("run route should include normalized param validation text.");
  process.exit(1);
}
if (!runRoute.includes("后端执行失败")) {
  console.error("run route should include normalized backend failure text.");
  process.exit(1);
}
if (!runsRoute.includes("run_id 不能为空")) {
  console.error("runs route should include normalized missing run_id text.");
  process.exit(1);
}
if (!runsRoute.includes("任务详情查询失败")) {
  console.error("runs route should include normalized detail query failure text.");
  process.exit(1);
}

console.log("web api error copy contract ok");
