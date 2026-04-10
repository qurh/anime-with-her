import { test, expect } from "@playwright/test";

test("home renders job list header", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Jobs")).toBeVisible();
});
