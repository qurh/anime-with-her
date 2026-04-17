const fs = require("fs");

function read(path) {
  return fs.readFileSync(path, "utf8");
}

const home = read("app/page.tsx");
const runs = read("app/runs/page.tsx");
const detail = read("app/runs/[runId]/page.tsx");
const api = read("lib/api.ts");
const runApiRoute = read("app/api/pipeline/run/route.ts");
const runDetailApiRoute = read("app/api/pipeline/runs/[runId]/route.ts");

const requiredTerms = [
  "创建任务",
  "任务历史",
  "任务详情",
  "失败原因",
  "重跑起点",
  "后端请求失败",
];

const joined = `${home}\n${runs}\n${detail}\n${api}`;
for (const term of requiredTerms) {
  if (!joined.includes(term)) {
    console.error("Missing normalized Chinese term:", term);
    process.exit(1);
  }
}

if (!runApiRoute.includes("创建任务失败，请稍后重试。")) {
  console.error("Missing normalized create-run API error copy");
  process.exit(1);
}

if (!runDetailApiRoute.includes("查询任务详情失败，请稍后重试。")) {
  console.error("Missing normalized run-detail API error copy");
  process.exit(1);
}

const mojibakeFragments = [
  "鍒涘缓",
  "浠诲姟",
  "璇︽儏",
  "鍚庣",
  "娴犺",
];

for (const fragment of mojibakeFragments) {
  if (joined.includes(fragment)) {
    console.error("Found mojibake fragment:", fragment);
    process.exit(1);
  }
}

console.log("web copy encoding contract ok");
