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

console.log("web run stage focus contract ok");
