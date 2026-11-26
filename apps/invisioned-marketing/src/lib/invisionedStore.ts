// SPDX-License-Identifier: MIT
import { promises as fs } from 'node:fs';
import path from 'node:path';

export interface PersistenceResult {
  mode: 'hybrid_cloud_and_jsonl' | 'jsonl_fallback';
  ledgerPath: string;
  cloudSynced: boolean;
  detail?: string;
}

export function escapeHtml(input: unknown): string {
  return String(input ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function resolveLedgerPath(filename: string): string {
  const isVercel = Boolean(process.env.VERCEL || process.env.AWS_LAMBDA_FUNCTION_NAME);
  if (isVercel) {
    return path.join('/tmp', filename);
  }
  return path.join(process.cwd(), '..', '..', '03_VAULT', 'runtime_state', filename);
}

/**
 * Hybrid non-volatile persistence:
 * 1. Always appends to local/ephemeral JSONL ledger (air-gapped sovereign fallback).
 * 2. When INVISIONED_DB_BRIDGE_URL is configured (e.g., Supabase/Neon/Prisma HTTP bridge),
 *    mirrors the record over HTTPS without blocking local commitment on network errors.
 */
export async function persistHybridRecord(
  collection: 'leads' | 'proposals',
  filename: string,
  record: Record<string, unknown>,
): Promise<PersistenceResult> {
  const ledgerPath = resolveLedgerPath(filename);
  await fs.mkdir(path.dirname(ledgerPath), { recursive: true });
  await fs.appendFile(ledgerPath, `${JSON.stringify(record)}\n`, 'utf-8');

  const bridgeUrl = process.env.INVISIONED_DB_BRIDGE_URL;
  if (!bridgeUrl) {
    return {
      mode: 'jsonl_fallback',
      ledgerPath,
      cloudSynced: false,
      detail: process.env.DATABASE_URL
        ? 'DATABASE_URL present; committed to JSONL ledger (set INVISIONED_DB_BRIDGE_URL for HTTP mirror).'
        : 'Air-gapped JSONL persistence active.',
    };
  }

  try {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (process.env.SALTARE_GATEWAY_TOKEN) {
      headers.Authorization = `Bearer ${process.env.SALTARE_GATEWAY_TOKEN}`;
    }
    const res = await fetch(bridgeUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({ collection, record }),
    });
    if (res.ok) {
      return { mode: 'hybrid_cloud_and_jsonl', ledgerPath, cloudSynced: true };
    }
    return {
      mode: 'jsonl_fallback',
      ledgerPath,
      cloudSynced: false,
      detail: `Cloud bridge HTTP ${res.status}; retained in JSONL ledger.`,
    };
  } catch (err) {
    return {
      mode: 'jsonl_fallback',
      ledgerPath,
      cloudSynced: false,
      detail: `Cloud bridge unreachable (${String(err)}); retained in JSONL ledger.`,
    };
  }
}

export async function readLedgerRecords<T = Record<string, unknown>>(filename: string): Promise<T[]> {
  const ledgerPath = resolveLedgerPath(filename);
  try {
    const data = await fs.readFile(ledgerPath, 'utf-8');
    return data
      .split('\n')
      .filter(Boolean)
      .map((line) => JSON.parse(line) as T);
  } catch {
    return [];
  }
}
