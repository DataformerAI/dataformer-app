import { expect, test } from "@playwright/test";
import path from "path";

test("dropDownComponent", async ({ page }) => {
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

  await page.getByTestId("extended-disclosure").click();
  await page.getByPlaceholder("Search").click();
  await page.getByPlaceholder("Search").fill("file");

  await page.waitForTimeout(1000);

  await page
    .getByTestId("dataFile")
    .first()
    .dragTo(page.locator('//*[@id="react-flow-id"]'));
  await page.mouse.up();
  await page.mouse.down();
  await page.getByTitle("fit view").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByTestId("icon-FileSearch2").click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles(path.join(__dirname, "/assets/test_file.txt"));
  await page.getByText("test_file.txt").isVisible();

  await page.getByPlaceholder("Search").click();
  await page.getByPlaceholder("Search").fill("text output");

  await page
    .getByTestId("outputsText Output")
    .first()
    .dragTo(page.locator('//*[@id="react-flow-id"]'));
  await page.mouse.up();
  await page.mouse.down();
  await page.getByTitle("fit view").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();

  // Click and hold on the first element
  await page
    .locator(
      '//*[@id="react-flow-id"]/div/div[1]/div[1]/div/div[2]/div[1]/div/div[2]/div[6]/button/div/div',
    )
    .hover();
  await page.mouse.down();

  // Move to the second element
  await page
    .locator(
      '//*[@id="react-flow-id"]/div/div[1]/div[1]/div/div[2]/div[2]/div/div[2]/div[3]/div/button/div/div',
    )
    .hover();

  // Release the mouse
  await page.mouse.up();

  await page.getByText("Playground", { exact: true }).click();
  await page.getByText("Run Flow", { exact: true }).click();
  await page.waitForTimeout(3000);
  const textOutput = await page.getByPlaceholder("Empty").first().inputValue();

  expect(textOutput).toContain("this is a test file");
});
