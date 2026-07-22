import { test, expect, Page } from "@playwright/test";

test("has correct title and content", async ({ page }: { page: Page }) => {
  await page.goto("/");
  await expect(page.locator("h1")).toContainText("KPIs Servicios");
  await expect(page.locator("text=Bootstrap completed successfully.")).toBeVisible();
});
