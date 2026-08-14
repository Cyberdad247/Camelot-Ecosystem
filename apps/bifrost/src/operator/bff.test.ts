// SPDX-License-Identifier: MIT

import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import type { Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import express from 'express';
import { createOperatorBff } from './bff';
import { InMemoryEventStore } from './receipts';
import { verifyManifest, issueLease } from './sentinel';
import type { EffectManifest } from './contracts';

let server: Server;
let base: string;

beforeAll(async () => {
  process.env.OPERATOR_SESSION_TOKEN = 'test-token';
  process.env.OPERATOR_FIXTURE_TASK = 'operator-console-approval';
  const app = express();
  app.use(express.json());
  const store = new InMemoryEventStore();
  const bff = createOperatorBff({
    store,
    verifyManifest,
    issueLease,
    now: () => new Date(),
    requiredEvidencePresent: (ref: string) => ref.startsWith('receipt://'),
    gideonVerdict: () => 'pass' as const,
    vfsEvidenceOk: () => true,
  });
  app.use('/v1/operator', bff);
  server = app.listen(0);
  await new Promise<void>((resolve) => server.once('listening', () => resolve()));
  base = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});

afterAll(async () => {
  await new Promise<void>((resolve) => server.close(() => resolve()));
});

describe('operator BFF', () => {
  it('rejects unauthenticated snapshot requests', async () => {
    const res = await fetch(`${base}/v1/operator/tasks/task_1/snapshot`);
    expect(res.status).toBe(401);
  });

  it('serves a typed task snapshot when authenticated', async () => {
    const res = await fetch(`${base}/v1/operator/tasks/task_1/snapshot`, {
      headers: { 'x-operator-token': 'test-token' },
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { schemaVersion: string; integrity: string; taskGraph: unknown[] };
    expect(body.schemaVersion).toBe('operator-task-snapshot/1');
    expect(body.integrity).toBe('verified');
    expect(Array.isArray(body.taskGraph)).toBe(true);
  });

  it('redacts sensitive fields from snapshot payloads', async () => {
    const res = await fetch(`${base}/v1/operator/tasks/task_1/snapshot`, {
      headers: { 'x-operator-token': 'test-token' },
    });
    const text = await res.text();
    expect(text).not.toContain('super-secret');
  });

  it('accepts a manifest-scoped approve decision and returns a lease', async () => {
    const res = await fetch(`${base}/v1/operator/effect-manifests/eff_1/decision`, {
      method: 'POST',
      headers: { 'x-operator-token': 'test-token', 'content-type': 'application/json' },
      body: JSON.stringify({ decision: 'approve', reason: 'evidence verified' }),
    });
    expect(res.status).toBe(200);
    const body = (await res.json()) as { status: string; lease?: { leaseId: string } };
    expect(body.status).toBe('APPROVED');
    expect(body.lease?.leaseId).toBeTruthy();
  });

  it('rejects a decision body with extra command/path fields', async () => {
    const res = await fetch(`${base}/v1/operator/effect-manifests/eff_1/decision`, {
      method: 'POST',
      headers: { 'x-operator-token': 'test-token', 'content-type': 'application/json' },
      body: JSON.stringify({ decision: 'approve', command: 'rm -rf /', paths: ['/etc'] }),
    });
    expect(res.status).toBe(400);
  });

  it('exposes an SSE event stream', async () => {
    const controller = new AbortController();
    const res = await fetch(`${base}/v1/operator/tasks/task_1/events`, {
      headers: { 'x-operator-token': 'test-token' },
      signal: controller.signal,
    });
    expect(res.status).toBe(200);
    expect(res.headers.get('content-type')).toContain('text/event-stream');
    // Close the stream so server.close() in afterAll can complete.
    controller.abort();
  });
});
