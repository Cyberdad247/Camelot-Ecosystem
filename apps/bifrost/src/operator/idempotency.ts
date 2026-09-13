// SPDX-License-Identifier: MIT

import { createHash } from 'node:crypto';

export type IdempotencyStatus = 'IN_FLIGHT' | 'COMMITTED' | 'REJECTED';
export type IdempotencyDecision = 'PROCEED' | 'REPLAY' | 'CONFLICT' | 'REJECTED';

export interface IdempotencyRecord {
  key: string;
  tenantId: string;
  manifestHash: string;
  correlationId: string;
  status: IdempotencyStatus;
  receiptRef?: string;
  responseBody?: string;
  expiresAt: number; // Unix timestamp in ms
  createdAt: number;
  updatedAt: number;
}

export class IdempotencyConflictError extends Error {
  constructor(
    public readonly key: string,
    public readonly tenantId: string,
    public readonly correlationId: string,
    message?: string,
  ) {
    super(message ?? `Operation '${key}' is already IN_FLIGHT under correlation '${correlationId}'.`);
    this.name = 'IdempotencyConflictError';
  }
}

/** Compute deterministic SHA-256 compound key: SHA256(client_key || tenant_id || manifest_hash). */
export function computeCompoundKey(key: string, tenantId: string, manifestHash: string): string {
  return createHash('sha256')
    .update(`${key}:${tenantId}:${manifestHash}`, 'utf8')
    .digest('hex');
}

/** FastMutex in-memory accelerator (<10s). */
export class FastMutexAccelerator {
  private locks = new Map<string, number>();

  constructor(private readonly defaultTtlMs = 10_000) {}

  tryAcquire(compoundKey: string, ttlMs?: number): boolean {
    const now = Date.now();
    const ttl = ttlMs ?? this.defaultTtlMs;
    const existingExp = this.locks.get(compoundKey);
    if (existingExp && existingExp > now) {
      return false;
    }
    this.locks.set(compoundKey, now + ttl);
    return true;
  }

  release(compoundKey: string): void {
    this.locks.delete(compoundKey);
  }

  isLocked(compoundKey: string): boolean {
    const now = Date.now();
    const exp = this.locks.get(compoundKey);
    if (!exp) return false;
    if (exp <= now) {
      this.locks.delete(compoundKey);
      return false;
    }
    return true;
  }
}

/** In-memory and WAL-compatible Idempotency store. */
export class InMemoryIdempotencyStore {
  private records = new Map<string, IdempotencyRecord>();

  get(compoundKey: string): IdempotencyRecord | undefined {
    return this.records.get(compoundKey);
  }

  insertInFlight(rec: IdempotencyRecord): boolean {
    const compoundKey = computeCompoundKey(rec.key, rec.tenantId, rec.manifestHash);
    const existing = this.records.get(compoundKey);
    const now = Date.now();
    if (existing) {
      if (existing.status === 'REJECTED' || existing.expiresAt <= now) {
        this.records.delete(compoundKey);
      } else {
        return false;
      }
    }
    this.records.set(compoundKey, rec);
    return true;
  }

  updateStatus(
    compoundKey: string,
    status: IdempotencyStatus,
    receiptRef?: string,
    responseBody?: string,
  ): IdempotencyRecord | undefined {
    const existing = this.records.get(compoundKey);
    if (!existing) return undefined;
    const updated: IdempotencyRecord = {
      ...existing,
      status,
      receiptRef: receiptRef ?? existing.receiptRef,
      responseBody: responseBody ?? existing.responseBody,
      updatedAt: Date.now(),
    };
    this.records.set(compoundKey, updated);
    return updated;
  }

  purgeExpired(): number {
    const now = Date.now();
    let count = 0;
    for (const [k, v] of this.records.entries()) {
      if (v.expiresAt <= now) {
        this.records.delete(k);
        count++;
      }
    }
    return count;
  }
}

/** TypeScript Idempotency Guardian coordinating FastMutex and Storage. */
export class IdempotencyGuardian {
  constructor(
    private readonly store = new InMemoryIdempotencyStore(),
    private readonly fastMutex = new FastMutexAccelerator(),
  ) {}

  acquireOrReplay(
    key: string,
    tenantId: string,
    manifestHash: string,
    correlationId: string,
    ttlMs = 300_000,
  ): { decision: IdempotencyDecision; record?: IdempotencyRecord } {
    const compoundKey = computeCompoundKey(key, tenantId, manifestHash);
    const now = Date.now();

    // 1. FastMutex check
    if (!this.fastMutex.tryAcquire(compoundKey, Math.min(ttlMs, 10_000))) {
      const existing = this.store.get(compoundKey);
      const cid = existing?.correlationId ?? correlationId;
      throw new IdempotencyConflictError(key, tenantId, cid, 'FastMutex burst collision: operation is in flight');
    }

    // 2. Check store
    const existing = this.store.get(compoundKey);
    if (existing) {
      if (existing.expiresAt <= now) {
        this.store.purgeExpired();
      } else if (existing.status === 'COMMITTED') {
        this.fastMutex.release(compoundKey);
        return { decision: 'REPLAY', record: existing };
      } else if (existing.status === 'IN_FLIGHT') {
        throw new IdempotencyConflictError(key, tenantId, existing.correlationId);
      }
    }

    // 3. Register IN_FLIGHT
    const rec: IdempotencyRecord = {
      key,
      tenantId,
      manifestHash,
      correlationId,
      status: 'IN_FLIGHT',
      expiresAt: now + ttlMs,
      createdAt: now,
      updatedAt: now,
    };

    const inserted = this.store.insertInFlight(rec);
    if (!inserted) {
      const ex = this.store.get(compoundKey);
      const cid = ex?.correlationId ?? correlationId;
      throw new IdempotencyConflictError(key, tenantId, cid, 'Durable store collision: operation is in flight');
    }

    return { decision: 'PROCEED', record: rec };
  }

  commit(
    key: string,
    tenantId: string,
    manifestHash: string,
    receiptRef: string,
    responseBody?: unknown,
  ): IdempotencyRecord {
    const compoundKey = computeCompoundKey(key, tenantId, manifestHash);
    const serialized =
      responseBody !== undefined
        ? typeof responseBody === 'string'
          ? responseBody
          : JSON.stringify(responseBody)
        : undefined;

    const updated = this.store.updateStatus(compoundKey, 'COMMITTED', receiptRef, serialized);
    this.fastMutex.release(compoundKey);
    if (!updated) {
      throw new Error(`No idempotency record found to commit for compound key: ${compoundKey}`);
    }
    return updated;
  }

  reject(key: string, tenantId: string, manifestHash: string, reason?: string): IdempotencyRecord {
    const compoundKey = computeCompoundKey(key, tenantId, manifestHash);
    const updated = this.store.updateStatus(compoundKey, 'REJECTED', undefined, reason);
    this.fastMutex.release(compoundKey);
    if (!updated) {
      throw new Error(`No idempotency record found to reject for compound key: ${compoundKey}`);
    }
    return updated;
  }
}
