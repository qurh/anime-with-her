const fs = require("fs");

const globalCssPath = "app/globals.css";
const layoutPath = "app/layout.tsx";

if (!fs.existsSync(globalCssPath)) {
  console.error("Missing file:", globalCssPath);
  process.exit(1);
}
if (!fs.existsSync(layoutPath)) {
  console.error("Missing file:", layoutPath);
  process.exit(1);
}

const css = fs.readFileSync(globalCssPath, "utf8");
const layout = fs.readFileSync(layoutPath, "utf8");

const requiredTokens = [
  "--color-bg",
  "--color-surface",
  "--color-border",
  "--color-text",
  "--color-primary",
  "--space-16",
  "--radius-md",
];

for (const token of requiredTokens) {
  if (!css.includes(token)) {
    console.error("Missing design token:", token);
    process.exit(1);
  }
}

if (!layout.includes("Noto_Sans_SC")) {
  console.error("layout.tsx should configure Noto_Sans_SC typography baseline.");
  process.exit(1);
}

console.log("web ui tokens contract ok");
