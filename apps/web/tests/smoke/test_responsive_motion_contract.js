const fs = require("fs");

const cssPath = "app/globals.css";
if (!fs.existsSync(cssPath)) {
  console.error("Missing file:", cssPath);
  process.exit(1);
}

const css = fs.readFileSync(cssPath, "utf8");

if (!css.includes("@media (prefers-reduced-motion: reduce)")) {
  console.error("globals.css should include prefers-reduced-motion fallback.");
  process.exit(1);
}

if (!css.includes("@media (max-width: 768px)")) {
  console.error("globals.css should include mobile/tablet responsive breakpoint.");
  process.exit(1);
}

if (!css.includes(".run-button")) {
  console.error("globals.css should style run-button touch target.");
  process.exit(1);
}

console.log("web responsive motion contract ok");
