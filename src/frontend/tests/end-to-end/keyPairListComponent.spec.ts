import { expect, test } from "@playwright/test";

test("KeypairListComponent", async ({ page }) => {
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
  await page.getByPlaceholder("Search").fill("amazon bedrock");

  await page.waitForTimeout(1000);

  await page
    .getByTestId("model_specsAmazon Bedrock")
    .dragTo(page.locator('//*[@id="react-flow-id"]'));
  await page.mouse.up();
  await page.mouse.down();
  await page.getByTitle("fit view").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();
  await page.getByTitle("zoom out").click();
  await page.locator('//*[@id="keypair0"]').click();
  await page.locator('//*[@id="keypair0"]').fill("testtesttesttest");
  await page.locator('//*[@id="keypair100"]').click();
  await page
    .locator('//*[@id="keypair100"]')
    .fill("test test test test test test");

  await page.getByTestId("div-generic-node").click();

  const valueWithSpace = await page.getByTestId("keypair100").inputValue();
  await page.getByTestId("div-generic-node").click();

  if (valueWithSpace !== "test test test test test test") {
    expect(false).toBeTruthy();
  }

  const plusButtonLocatorNode = page.locator('//*[@id="plusbtn0"]');
  const elementCountNode = await plusButtonLocatorNode?.count();
  if (elementCountNode > 0) {
    await plusButtonLocatorNode.click();
  }
  await page.getByTestId("div-generic-node").click();

  await page.locator('//*[@id="keypair0"]').click();
  await page.locator('//*[@id="keypair0"]').fill("testtesttesttest1");
  await page.getByTestId("div-generic-node").click();

  const keyPairVerification = page.locator('//*[@id="keypair100"]');
  const elementKeyCount = await keyPairVerification?.count();

  if (elementKeyCount === 1) {
    expect(true).toBeTruthy();
  } else {
    expect(false).toBeTruthy();
  }

  await page.getByTestId("more-options-modal").click();
  await page.getByTestId("edit-button-modal").click();

  await page.locator('//*[@id="showcache"]').click();
  expect(await page.locator('//*[@id="showcache"]').isChecked()).toBeFalsy();
  await page.locator('//*[@id="showcredentials_profile_name"]').click();
  expect(
    await page.locator('//*[@id="showcredentials_profile_name"]').isChecked(),
  ).toBeFalsy();
  await page.locator('//*[@id="saveChangesBtn"]').click();

  const plusButtonLocator = page.locator('//*[@id="plusbtn0"]');
  const elementCount = await plusButtonLocator?.count();
  if (elementCount === 0) {
    expect(true).toBeTruthy();
    await page.getByTestId("div-generic-node").click();

    await page.getByTestId("more-options-modal").click();
    await page.getByTestId("edit-button-modal").click();

    await page.locator('//*[@id="showcredentials_profile_name"]').click();
    expect(
      await page.locator('//*[@id="showcredentials_profile_name"]').isChecked(),
    ).toBeTruthy();
    await page.locator('//*[@id="showcache"]').click();
    expect(await page.locator('//*[@id="showcache"]').isChecked()).toBeTruthy();

    await page.locator('//*[@id="editNodekeypair0"]').click();
    await page.locator('//*[@id="editNodekeypair0"]').fill("testtesttesttest");

    const keyPairVerification = page.locator('//*[@id="editNodekeypair0"]');
    const elementKeyCount = await keyPairVerification?.count();

    if (elementKeyCount === 1) {
      await page.locator('//*[@id="saveChangesBtn"]').click();

      await page.getByTestId("div-generic-node").click();

      const key1 = await page.locator('//*[@id="keypair0"]').inputValue();
      const value1 = await page.locator('//*[@id="keypair100"]').inputValue();
      await page.getByTestId("div-generic-node").click();

      if (
        key1 === "testtesttesttest" &&
        value1 === "test test test test test test"
      ) {
        expect(true).toBeTruthy();
      } else {
        expect(false).toBeTruthy();
      }
    } else {
      expect(false).toBeTruthy();
    }
  } else {
    expect(false).toBeTruthy();
  }
});
