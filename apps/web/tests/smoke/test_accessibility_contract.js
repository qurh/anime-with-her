const fs = require("fs");

const files = ["app/page.tsx", "app/runs/[runId]/page.tsx"];

for (const filePath of files) {
  if (!fs.existsSync(filePath)) {
    console.error("Missing file:", filePath);
    process.exit(1);
  }
}

const home = fs.readFileSync("app/page.tsx", "utf8");
const detail = fs.readFileSync("app/runs/[runId]/page.tsx", "utf8");

if (!home.includes('role="alert"')) {
  console.error("Home page should use role=alert for error feedback.");
  process.exit(1);
}
if (!detail.includes('role="alert"')) {
  console.error("Run detail page should use role=alert for error feedback.");
  process.exit(1);
}
if (!detail.includes('aria-live="polite"')) {
  console.error("Run detail page should expose aria-live polite status updates.");
  process.exit(1);
}

console.log("web accessibility contract ok");
