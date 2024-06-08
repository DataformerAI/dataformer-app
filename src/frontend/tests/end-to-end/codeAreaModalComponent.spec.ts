import { test } from "@playwright/test";

test("CodeAreaModalComponent", async ({ page }) => {
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
  await page.getByPlaceholder("Search").fill("python function");

  await page.waitForTimeout(1000);

  await page
    .getByTestId("experimentalPython Function")
    .dragTo(page.locator('//*[@id="react-flow-id"]'));
  await page.mouse.up();
  await page.mouse.down();
  await page.getByTitle("fit view").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();
  await page.getByTestId("div-generic-node").click();
  await page.getByTestId("code-button-modal").click();

  const wCode =
    'def python_function(text: str) -> st:    """This is a default python function that returns the input text"""    return text';

  const customComponentCode = `from typing import Callable
from dfapp.field_typing import Code
from dfapp.interface.custom.custom_component import CustomComponent
from dfapp.interface.custom.utils import get_function

class PythonFunctionComponent(CustomComponent):
    def python_function(text: str) -> str:
        """This is a default python function that returns the input text"""
        return text`;

  await page
    .locator("#CodeEditor div")
    .filter({ hasText: "PythonFunctionComponent" })
    .nth(1)
    .click();
  await page.locator("textarea").press("Control+a");
  await page.locator("textarea").fill(wCode);
  await page.locator('//*[@id="checkAndSaveBtn"]').click();
  await page.waitForTimeout(1000);
  // expect(
  //   await page.getByText("invalid syntax (<unknown>, line 1)").isVisible()
  // ).toBeTruthy();
  await page.locator("textarea").press("Control+a");
  await page.locator("textarea").fill(wCode);
  await page.locator("textarea").fill(customComponentCode);
  await page.locator('//*[@id="checkAndSaveBtn"]').click();
  await page.waitForTimeout(1000);

  // await page.getByTestId("code-button-modal").click();
  // const inputCodeValue = await page
  //   .locator('//*[@id="codeValue"]')
  //   .inputValue();

  // expect(inputCodeValue).toContain("def python_function(text: str) -> str");
});
