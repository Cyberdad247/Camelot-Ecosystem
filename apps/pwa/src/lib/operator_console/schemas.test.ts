// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { OperatorTaskSnapshotSchema, EvidenceEnvelopeSchema } from './schemas';

describe('operator console client schemas', () => {
  it('parses a valid snapshot payload', () => {
    const parsed = OperatorTaskSnapshotSchema.parse({
      schemaVersion: 'operator-task-snapshot/1',
      taskId: 'task_1',
      correlationId: 'cor_1',
      generatedAt: '2026-08-14T13:48:00Z',
      integrity: 'verified',
      intent: {}, approval: {}, taskGraph: [], diffs: [], tests: [], receipts: [],
    });
    expect(parsed.integrity).toBe('verified');
  });

  it('rejects an unknown schemaVersion (drift guard)', () => {
    expect(() => OperatorTaskSnapshotSchema.parse({
      schemaVersion: 'operator-task-snapshot/2',
      taskId: 'task_1', correlationId: 'cor_1', generatedAt: 'x', integrity: 'verified',
    })).toThrow();
  });

  it('parses an evidence envelope with receipt reference', () => {
    const envelope = EvidenceEnvelopeSchema.parse({
      schemaVersion: 'operator-evidence/1',
      eventId: 'evt_123',
      taskId: 'task_1',
      correlationId: 'cor_1',
      timestamp: '2026-08-14T13:48:00Z',
      actor: { id: 'sentinel', role: 'sentinel' },
      kind: 'decision.approved',
      payload: { leaseId: 'lease_abc' },
      payloadHash: 'sha256:abc',
      integrity: 'verified',
      receiptRef: 'receipt://sentinel/lease/lease_abc',
    });
    expect(envelope.schemaVersion).toBe('operator-evidence/1');
    expect(envelope.receiptRef).toBe('receipt://sentinel/lease/lease_abc');
  });

  it('parses snapshot with typed diff & test receipt references', () => {
    const parsed = OperatorTaskSnapshotSchema.parse({
      schemaVersion: 'operator-task-snapshot/1',
      taskId: 'task_1',
      correlationId: 'cor_1',
      generatedAt: '2026-08-14T13:48:00Z',
      integrity: 'verified',
      intent: {}, approval: {}, taskGraph: [],
      diffs: [{
        baseRevision: 'base',
        candidateRevision: 'cand',
        diffSha256: 'sha256:abc',
        changedPaths: ['apps/pwa/src/app.tsx'],
        addedLines: 5,
        removedLines: 2,
        generatedAt: '2026-08-14T13:48:00Z',
        gideonVerdict: 'pass',
        receiptRef: 'receipt://vfs/diff/01abc',
      }],
      tests: [{
        schemaVersion: 'test-run-result/1',
        runId: 'run_1',
        taskId: 'task_1',
        correlationId: 'cor_1',
        runner: 'boris-gideon-adapter',
        status: 'passed',
        startedAt: '2026-08-14T13:48:00Z',
        suites: [{
          name: 'unit',
          status: 'passed',
          durationMs: 120,
          artifactRef: 'receipt://boris/test-report/run_1',
        }],
        summary: { total: 1, passed: 1, failed: 0, skipped: 0 },
        outputHash: 'sha256:out',
        receiptRef: 'receipt://boris/test-run/run_1',
      }],
      receipts: [],
    });
    expect(parsed.diffs[0].receiptRef).toBe('receipt://vfs/diff/01abc');
    expect(parsed.tests[0].receiptRef).toBe('receipt://boris/test-run/run_1');
    expect(parsed.tests[0].suites[0].artifactRef).toBe('receipt://boris/test-report/run_1');
  });
});
