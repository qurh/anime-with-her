const fs = require("fs");

const detailPath = "app/runs/[runId]/page.tsx";
const skeletonPath = "app/components/LoadingSkeleton.tsx";
const cssPath = "app/globals.css";

for (const p of [detailPath, skeletonPath, cssPath]) {
  if (!fs.existsSync(p)) {
    console.error("Missing file:", p);
    process.exit(1);
  }
}

const detail = fs.readFileSync(detailPath, "utf8");
const css = fs.readFileSync(cssPath, "utf8");

if (!detail.includes("LoadingSkeleton")) {
  console.error("Run detail page should use LoadingSkeleton.");
  process.exit(1);
}
if (!css.includes(".skeleton")) {
  console.error("globals.css should include .skeleton styles.");
  process.exit(1);
}

console.log("web skeleton contract ok");
