const fs = require("fs");

const homePath = "app/page.tsx";
if (!fs.existsSync(homePath)) {
  console.error("Missing home page:", homePath);
  process.exit(1);
}

const home = fs.readFileSync(homePath, "utf8");

if (!home.includes("预计处理时长")) {
  console.error("Home page should include estimated duration guidance.");
  process.exit(1);
}
if (!home.includes("创建后将自动跳转")) {
  console.error("Home page should include auto-redirect feedback.");
  process.exit(1);
}

console.log("web home feedback contract ok");
