const fs = require("fs");

const runDetailPath = "app/runs/[runId]/page.tsx";
const runProxyPath = "app/api/pipeline/run/route.ts";

if (!fs.existsSync(runDetailPath)) {
  console.error("Missing file:", runDetailPath);
  process.exit(1);
}
if (!fs.existsSync(runProxyPath)) {
  console.error("Missing file:", runProxyPath);
  process.exit(1);
}

const detailContent = fs.readFileSync(runDetailPath, "utf8");
if (!detailContent.includes("从失败阶段重跑")) {
  console.error("Run detail page should expose retry entry.");
  process.exit(1);
}
if (!detailContent.includes("start_stage")) {
  console.error("Run detail page should pass start_stage.");
  process.exit(1);
}

const proxyContent = fs.readFileSync(runProxyPath, "utf8");
if (!proxyContent.includes("start_stage")) {
  console.error("Pipeline run proxy should forward start_stage.");
  process.exit(1);
}

console.log("web run retry contract ok");
