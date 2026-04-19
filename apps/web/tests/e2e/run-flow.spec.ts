import { expect, test } from "@playwright/test";

import { installMockPipelineApi } from "./fixtures/mock-backend";

test("create -> detail -> retry flow", async ({ page }) => {
  await installMockPipelineApi(page);

  await page.goto("/");
  await expect(page.getByRole("heading", { name: "AI 配音导演台" })).toBeVisible();

  await page.getByRole("button", { name: "创建任务" }).click();

  await expect(page).toHaveURL(/\/runs\/run_100\?episode_id=episode_1/);
  await expect(page.getByRole("heading", { name: "任务详情" })).toBeVisible();
  await expect(page.getByText("失败原因：mock tts timeout")).toBeVisible();
  await expect(page.getByRole("heading", { name: "质量评分" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "阶段告警" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "成本摘要" })).toBeVisible();

  await page.getByRole("button", { name: "提交重跑" }).click();

  await expect(page).toHaveURL(/\/runs\/run_101\?episode_id=episode_1/);
  await expect(page.getByText(/任务状态：\s*已完成/)).toBeVisible();
});
