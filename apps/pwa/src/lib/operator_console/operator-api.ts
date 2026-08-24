// SPDX-License-Identifier: MIT

'use client';

import { OperatorTaskSnapshotSchema, type OperatorTaskSnapshot } from './schemas';

const BFF_BASE = process.env.NEXT_PUBLIC_BIFROST_HTTP_URL ?? 'http://localhost:3001';

export class OperatorApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'OperatorApiError';
  }
}

function headers(): Record<string, string> {
  const h: Record<string, string> = { 'content-type': 'application/json' };
  const token = localStorage.getItem('operator-session-token') ?? undefined;
  if (token) h['x-operator-token'] = token;
  return h;
}

export async function fetchSnapshot(taskId: string): Promise<OperatorTaskSnapshot> {
  const res = await fetch(`${BFF_BASE}/v1/operator/tasks/${taskId}/snapshot`, { headers: headers() });
  if (res.status === 401) throw new OperatorApiError(401, 'operator session required');
  if (!res.ok) throw new OperatorApiError(res.status, `snapshot failed: ${res.status}`);
  const body = OperatorTaskSnapshotSchema.parse(await res.json());
  return body;
}

export interface DecisionResponse {
  status: 'APPROVED' | 'DENIED' | 'BLOCKED';
  manifestId: string;
  lease?: { leaseId: string };
  reasons?: string[];
}

export async function submitDecision(
  manifestId: string,
  decision: 'approve' | 'deny',
  reason?: string,
): Promise<DecisionResponse> {
  const res = await fetch(`${BFF_BASE}/v1/operator/effect-manifests/${manifestId}/decision`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({ decision, reason }),
  });
  if (res.status === 401) throw new OperatorApiError(401, 'operator session required');
  if (!res.ok) throw new OperatorApiError(res.status, `decision failed: ${res.status}`);
  return (await res.json()) as DecisionResponse;
}
