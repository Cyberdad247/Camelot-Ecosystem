// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { OperatorTaskSnapshotSchema } from './schemas';

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
});
