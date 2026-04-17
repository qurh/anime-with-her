const fs = require("fs");

const cssPath = "app/globals.css";
if (!fs.existsSync(cssPath)) {
  console.error("Missing css file:", cssPath);
  process.exit(1);
}

const css = fs.readFileSync(cssPath, "utf8");

if (!css.includes("--motion-fast: 120ms")) {
  console.error("CSS should define --motion-fast: 120ms.");
  process.exit(1);
}
if (!css.includes("--motion-normal: 200ms")) {
  console.error("CSS should define --motion-normal: 200ms.");
  process.exit(1);
}
if (!css.includes("--motion-slow: 240ms")) {
  console.error("CSS should define --motion-slow: 240ms.");
  process.exit(1);
}
if (!css.includes("prefers-reduced-motion")) {
  console.error("CSS should include prefers-reduced-motion fallback.");
  process.exit(1);
}
if (!css.includes("min-height: 44px")) {
  console.error("CSS should guarantee 44px touch targets.");
  process.exit(1);
}
if (!css.includes("transition")) {
  console.error("CSS should include interaction transition definitions.");
  process.exit(1);
}

console.log("web interaction motion contract ok");
