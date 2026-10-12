import { expect, test } from '@playwright/test';

test('cognitive cartridge loads without stale dynamic import failures', async ({ page }) => {
  const browserErrors: string[] = [];
  const failedAssetRequests: string[] = [];

  page.on('pageerror', (error) => {
    browserErrors.push(error.message);
  });

  page.on('console', (message) => {
    if (message.type() === 'error') {
      browserErrors.push(message.text());
    }
  });

  page.on('requestfailed', (request) => {
    if (request.url().includes('/assets/')) {
      failedAssetRequests.push(`${request.url()} ${request.failure()?.errorText ?? ''}`.trim());
    }
  });

  await page.goto('/cartridge/cognitive', { waitUntil: 'networkidle' });

  await expect(page).toHaveTitle(/Anya Dashboard/i);
  await expect(page.getByRole('heading', { name: /Cognitive Command Deck/i })).toBeVisible();
  await expect(page.locator('.vite-error-overlay, [data-nextjs-dialog]')).toHaveCount(0);
  expect(failedAssetRequests).toEqual([]);
  expect(browserErrors.join('\n')).not.toMatch(
    /Failed to fetch dynamically imported module|vite-error-overlay/i,
  );
});

test('camelot os command surface reads local orchestration and memory tiers', async ({ page }) => {
  await page.goto('/camelot-os', { waitUntil: 'networkidle' });

  await expect(page.getByRole('heading', { name: /Camelot OS Command/i })).toBeVisible();
  await expect(page.getByText(/Strategic Orchestration/i)).toBeVisible();
  await expect(page.getByText(/Cloudbrain Memory Routing/i)).toBeVisible();
  await expect(page.getByText(/Current dashboard session, websocket events/i)).toBeVisible();
  await expect(page.getByText(/NotebookLM synthesis/i)).toBeVisible();
  await expect(page.getByText(/Permanent archive/i)).toBeVisible();
  await expect(page.getByText(/Root Provenance/i)).toBeVisible();
});

test('break-glass support route renders token validation surface', async ({ page }) => {
  await page.goto('/support/test', { waitUntil: 'networkidle' });

  await expect(page.getByRole('heading', { name: /Break-Glass Support/i })).toBeVisible();
  await expect(page.getByLabel(/Temporary token/i)).toBeVisible();
  await expect(page.getByRole('button', { name: /Unlock Support Session/i })).toBeDisabled();
});
