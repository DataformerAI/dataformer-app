import { expect, test } from "@playwright/test";

test("flowSettings", async ({ page }) => {
  await page.goto("/");
  await page.waitForTimeout(2000);

  let modalCount = 0;
  try {
    const modalTitleElement = await page?.getByTestId("modal-title");
    if (modalTitleElement) {
      modalCount = await modalTitleElement.count();
    }
  } catch (error) {
    modalCount = 0;
  }

  while (modalCount === 0) {
    await page.locator('//*[@id="new-project-btn"]').click();
    await page.waitForTimeout(5000);
    modalCount = await page.getByTestId("modal-title")?.count();
  }
  await page.waitForTimeout(1000);

  await page.getByTestId("blank-flow").click();
  await page.waitForTimeout(1000);

  await page.getByTestId("flow_name").click();
  await page.getByText("Settings").first().click();
  await page
    .getByPlaceholder("Flow name")
    .fill(
      "Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test",
    );

  await page.getByText("Character limit reached").isVisible();

  await page.getByPlaceholder("Flow name").click();
  const randomName = Math.random().toString(36).substring(2);
  await page.getByPlaceholder("Flow name").fill(randomName);
  await page.getByPlaceholder("Flow name").click();
  await page
    .getByPlaceholder("Flow description")
    .fill(
      "Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test",
    );

  await page.getByText("Save").last().click();

  await page.waitForTimeout(1000);

  await page.getByText("Changes saved successfully").isVisible();

  await page.getByTestId("flow_name").click();
  await page.getByText("Settings").first().click();

  const flowName = await page.getByPlaceholder("Flow name").inputValue();
  const flowDescription = await page
    .getByPlaceholder("Flow description")
    .inputValue();

  if (flowName != randomName) {
    expect(false).toBeTruthy();
  }

  if (
    flowDescription !=
    "Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test Flow Name Test"
  ) {
    expect(false).toBeTruthy();
  }
  await page.getByText("Saved").first().isVisible();
  await page.getByTestId("icon-CheckCircle2").first().isVisible();
});
