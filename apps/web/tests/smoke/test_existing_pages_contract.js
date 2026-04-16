const fs = require("fs");

const checks = [
  ["app/page.tsx", "AI 配音导演台"],
  ["app/episodes/[episodeId]/character-review/page.tsx", "角色分析确认"],
  ["app/episodes/[episodeId]/segments/page.tsx", "关键片段精修"],
];

for (const [filePath, text] of checks) {
  if (!fs.existsSync(filePath)) {
    console.error("Missing file:", filePath);
    process.exit(1);
  }
  const content = fs.readFileSync(filePath, "utf8");
  if (!content.includes(text)) {
    console.error("Missing text:", text, "in", filePath);
    process.exit(1);
  }
}

console.log("web existing pages contract ok");
