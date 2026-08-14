// SPDX-License-Identifier: MIT

import type { EvidenceEnvelope } from './schemas';

/** Key-sorted canonical JSON — must match apps/bifrost/src/operator/chain.ts. */
export function canonicalJson(value: unknown): string {
  return JSON.stringify(sortKeys(value));
}

function sortKeys(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortKeys);
  if (value !== null && typeof value === 'object') {
    const record = value as Record<string, unknown>;
    const out: Record<string, unknown> = {};
    for (const key of Object.keys(record).sort()) out[key] = sortKeys(record[key]);
    return out;
  }
  return value;
}

async function digestHex(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const buf = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export async function payloadHash(payload: unknown): Promise<string> {
  return `sha256:${await digestHex(canonicalJson(payload))}`;
}

/** Recompute the payload hash and compare against the envelope's claim. */
export async function verifyEnvelope(envelope: EvidenceEnvelope): Promise<boolean> {
  const expected = await payloadHash(envelope.payload);
  return expected === envelope.payloadHash;
}
