// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import {
  FastMutexAccelerator,
  IdempotencyConflictError,
  IdempotencyGuardian,
  computeCompoundKey,
} from './idempotency';

describe('IdempotencyGuardian TS', () => {
  it('computes distinct compound keys across tenants and manifests', () => {
    const k1 = computeCompoundKey('key_1', 'tenant_a', 'sha256:1111');
    const k2 = computeCompoundKey('key_1', 'tenant_a', 'sha256:1111');
    const k3 = computeCompoundKey('key_1', 'tenant_b', 'sha256:1111');
    const k4 = computeCompoundKey('key_1', 'tenant_a', 'sha256:2222');

    expect(k1).toBe(k2);
    expect(k1).not.toBe(k3);
    expect(k1).not.toBe(k4);
    expect(k1).toHaveLength(64);
  });

  it('handles fast mutex lock/release', () => {
    const mutex = new FastMutexAccelerator(100);
    expect(mutex.tryAcquire('lock_1')).toBe(true);
    expect(mutex.isLocked('lock_1')).toBe(true);
    expect(mutex.tryAcquire('lock_1')).toBe(false);

    mutex.release('lock_1');
    expect(mutex.isLocked('lock_1')).toBe(false);
    expect(mutex.tryAcquire('lock_1')).toBe(true);
  });

  it('runs complete proceed-commit-replay lifecycle', () => {
    const guardian = new IdempotencyGuardian();
    const key = 'uuid7_001';
    const tenantId = 'tenant_alpha';
    const manifest = 'sha256:abc';

    // 1. Ingress PROCEED
    const first = guardian.acquireOrReplay(key, tenantId, manifest, 'cor_1');
    expect(first.decision).toBe('PROCEED');
    expect(first.record?.status).toBe('IN_FLIGHT');

    // 2. Conflict
    expect(() => guardian.acquireOrReplay(key, tenantId, manifest, 'cor_2')).toThrow(
      IdempotencyConflictError,
    );

    // 3. Commit
    const committed = guardian.commit(key, tenantId, manifest, 'rcp_123', { status: 'OK' });
    expect(committed.status).toBe('COMMITTED');
    expect(committed.receiptRef).toBe('rcp_123');

    // 4. Replay
    const replay = guardian.acquireOrReplay(key, tenantId, manifest, 'cor_3');
    expect(replay.decision).toBe('REPLAY');
    expect(replay.record?.receiptRef).toBe('rcp_123');
  });

  it('strictly isolates identical keys across different tenants', () => {
    const guardian = new IdempotencyGuardian();
    const key = 'shared_key';
    const manifest = 'sha256:xyz';

    const tA = guardian.acquireOrReplay(key, 'tenant_a', manifest, 'cor_a');
    const tB = guardian.acquireOrReplay(key, 'tenant_b', manifest, 'cor_b');

    expect(tA.decision).toBe('PROCEED');
    expect(tB.decision).toBe('PROCEED');

    guardian.commit(key, 'tenant_a', manifest, 'rcp_a');

    const replayA = guardian.acquireOrReplay(key, 'tenant_a', manifest, 'cor_a2');
    expect(replayA.decision).toBe('REPLAY');

    expect(() => guardian.acquireOrReplay(key, 'tenant_b', manifest, 'cor_b2')).toThrow(
      IdempotencyConflictError,
    );
  });
});
