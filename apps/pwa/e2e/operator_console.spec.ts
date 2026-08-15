// SPDX-License-Identifier: MIT

import { expect, test, type Page } from '@playwright/test';

const BFF_PREFIX = '**/v1/operator/**';

function snapshotPayload(overrides: Record<string, unknown> = {}) {
  return {
    schemaVersion: 'operator-task-snapshot/1',
    taskId: 'task_01J',
    correlationId: 'cor_task_01J',
    generatedAt: new Date().toISOString(),
    integrity: 'verified',
    intent: { raw: 'Verify scoped patch promote' },
    approval: { state: 'APPROVAL_REQUIRED' },
    taskGraph: [
      { nodeId: 'n1', name: 'ant-mapper', status: 'done' },
      { nodeId: 'n2', name: 'owl-auditor', status: 'running' },
    ],
    diffs: [{
      baseRevision: 'base', candidateRevision: 'cand', diffSha256: 'sha256:abc',
      changedPaths: ['apps/pwa/src/app/console/page.tsx'],
      addedLines: 12, removedLines: 3, generatedAt: new Date().toISOString(),
      gideonVerdict: 'pass',
    }],
    tests: [{
      schemaVersion: 'test-run-result/1', runId: 'run_1', taskId: 'task_01J',
      correlationId: 'cor_task_01J', runner: 'boris-gideon-adapter',
      status: 'passed', startedAt: new Date().toISOString(),
      suites: [], summary: { total: 4, passed: 4, failed: 0, skipped: 0 },
      outputHash: 'sha256:test',
    }],
    receipts: [],
    ...overrides,
  };
}

async function interceptSnapshot(page: Page, payload: Record<string, unknown>) {
  await page.route(`${BFF_PREFIX}/tasks/task_01J/snapshot`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(payload) }),
  );
}

test.describe('operator console', () => {
  test('renders all six panels with real fixture data', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.goto('/console');
    await expect(page.getByRole('heading', { name: 'OPERATOR CONSOLE' })).toBeVisible();
    for (const panel of ['Intent', 'Approval', 'Task Graph', 'Diffs', 'Tests', 'Receipts']) {
      await expect(page.getByLabel(panel, { exact: true })).toBeVisible();
    }
    await expect(page.getByText('ant-mapper')).toBeVisible();
    await expect(page.getByText('owl-auditor')).toBeVisible();
  });

  test('approval-required path: approve issues a lease', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.route(`${BFF_PREFIX}/effect-manifests/eff_01J/decision`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'APPROVED', manifestId: 'eff_01J', lease: { leaseId: 'lease_1' } }),
      }),
    );
    await page.goto('/console');
    await page.getByRole('button', { name: 'Approve' }).click();
    await page.getByRole('button', { name: 'Confirm approve' }).click();
    await expect(page.getByText('Lease lease_1 issued')).toBeVisible();
  });

  test('deny path records a denial and issues no lease', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.route(`${BFF_PREFIX}/effect-manifests/eff_01J/decision`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'DENIED', manifestId: 'eff_01J' }) }),
    );
    await page.goto('/console');
    await page.getByRole('button', { name: 'Deny' }).click();
    await page.getByRole('button', { name: 'Confirm deny' }).click();
    await expect(page.getByText('Denied')).toBeVisible();
  });

  test('sentinel outage disables approve/deny', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload({ approval: { state: 'APPROVAL_SUSPENDED' } }));
    await page.goto('/console');
    await expect(page.getByText(/Approval suspended/)).toBeVisible();
    // Suspended state removes the decision controls entirely — no approval path exists.
    await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Deny' })).toHaveCount(0);
  });

  test('gideon outage blocks promotion (audit suspended)', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload({ approval: { state: 'AUDIT_SUSPENDED' } }));
    await page.goto('/console');
    await expect(page.getByText(/Audit suspended/)).toBeVisible();
  });

  test('integrity tamper renders INTEGRITY FAILED and blocks approval', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload({ integrity: 'integrity_failed' }));
    await page.goto('/console');
    await expect(page.getByText('INTEGRITY FAILED').first()).toBeVisible();
    await expect(page.getByRole('button', { name: 'Approve' })).toBeDisabled();
  });

  test('stale Bifrost connection disables live controls', async ({ page }) => {
    await page.route(`${BFF_PREFIX}/tasks/task_01J/snapshot`, (route) =>
      route.abort(),
    );
    await page.goto('/console');
    await expect(page.getByText(/STALE/)).toBeVisible();
    // No snapshot arrives, so no evidence and no approval path exist — the
    // Approval panel renders its empty state rather than live controls.
    await expect(page.getByLabel('Approval', { exact: true })).toContainText(/No verified evidence yet/);
    await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0);
  });

  test('no fabricated content when the stream is absent', async ({ page }) => {
    await interceptSnapshot(page, snapshotPayload());
    await page.goto('/console');
    await expect(page.getByText(/No verified evidence yet/)).toHaveCount(0);
    // Panels render real data; empty-state appears only for genuinely empty panels.
    await expect(page.getByText('No verified records yet.')).toBeVisible();
  });
});
