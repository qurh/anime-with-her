const fs = require("fs");

const layoutPath = "app/layout.tsx";
const pages = ["app/page.tsx", "app/runs/page.tsx", "app/runs/[runId]/page.tsx"];

if (!fs.existsSync(layoutPath)) {
  console.error("Missing layout file:", layoutPath);
  process.exit(1);
}

const layout = fs.readFileSync(layoutPath, "utf8");
if (!layout.includes("跳到主内容")) {
  console.error("Layout should include skip link copy: 跳到主内容.");
  process.exit(1);
}
if (!layout.includes('href="#main-content"')) {
  console.error("Layout should include skip link target #main-content.");
  process.exit(1);
}

for (const pagePath of pages) {
  if (!fs.existsSync(pagePath)) {
    console.error("Missing page file:", pagePath);
    process.exit(1);
  }
  const page = fs.readFileSync(pagePath, "utf8");
  if (!page.includes('<main id="main-content"')) {
    console.error("Page should include main landmark id=main-content:", pagePath);
    process.exit(1);
  }
}

console.log("web a11y landmark contract ok");
