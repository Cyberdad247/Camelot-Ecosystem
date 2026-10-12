import { chromium } from 'playwright';

const SCREEN_DIR = process.argv[2];
const browser = await chromium.launch({ args: ['--no-sandbox'] });
const page = await browser.newPage();
const consoleErrors = [];
page.on('console', (msg) => {
  if (msg.type() === 'error') consoleErrors.push(msg.text());
});
page.on('pageerror', (err) => consoleErrors.push(String(err)));

await page.goto('http://localhost:5183/', { waitUntil: 'load', timeout: 30000 });

await page.waitForSelector('text=Live Fleet', { timeout: 15000 });
await page.waitForSelector('text=Config', { timeout: 15000 });
// Let the 15s-poll fleet fetch and initial config fetch settle.
await page.waitForTimeout(1500);

await page.screenshot({ path: `${SCREEN_DIR}/01_hub_initial.png`, fullPage: true });

const fleetText = await page
  .locator('text=Live Fleet')
  .locator('xpath=ancestor::div[contains(@class,"rounded-xl")]')
  .first()
  .innerText();
const configText = await page
  .locator('text=Config')
  .locator('xpath=ancestor::div[contains(@class,"rounded-xl")]')
  .first()
  .innerText();

console.log('--- FLEET PANEL TEXT ---');
console.log(fleetText);
console.log('--- CONFIG PANEL TEXT ---');
console.log(configText);

// Interact: change sync_interval to 3, save, confirm, then set back to 0, save.
const intervalInput = page.locator('input[type="number"]').first();
await intervalInput.fill('3');
const saveButton = page.getByRole('button', { name: /save/i });
await saveButton.click();
await page.waitForSelector('[aria-label="Saved"]', { timeout: 8000 });
await page.screenshot({ path: `${SCREEN_DIR}/02_after_save_3.png`, fullPage: true });
console.log('SAVE_3_OK');

// Safety: revert to 0 immediately.
await intervalInput.fill('0');
await saveButton.click();
await page.waitForSelector('[aria-label="Saved"]', { timeout: 8000 });
const revertedValue = await intervalInput.inputValue();
console.log('REVERTED_INTERVAL_VALUE=' + revertedValue);
await page.screenshot({ path: `${SCREEN_DIR}/03_after_revert_0.png`, fullPage: true });

console.log('--- CONSOLE ERRORS ---');
console.log(JSON.stringify(consoleErrors, null, 2));

await browser.close();
