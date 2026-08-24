// SPDX-License-Identifier: MIT

import { describe, expect, it } from 'vitest';
import { payloadHash, verifyEnvelope } from './integrity';
import type { EvidenceEnvelope } from './schemas';

function envelope(overrides: Partial<EvidenceEnvelope> = {}): EvidenceEnvelope {
  const payload = { decision: 'approve' };
  return {
    schemaVersion: 'operator-evidence/1',
    eventId: 'evt_1', taskId: 'task_1', correlationId: 'cor_1',
    timestamp: '2026-08-14T13:48:00Z',
    actor: { id: 'sentinel', role: 'sentinel' },
    kind: 'decision.approved', payload,
    payloadHash: 'sha256:placeholder', // replaced below with the real hash
    integrity: 'verified',
    ...overrides,
  };
}

describe('client integrity', () => {
  it('verifies a self-consistent envelope', async () => {
    const evt = envelope();
    evt.payloadHash = await payloadHash(evt.payload);
    expect(await verifyEnvelope(evt)).toBe(true);
  });

  it('fails when payloadHash does not match the payload', async () => {
    expect(await verifyEnvelope(envelope({ payloadHash: 'sha256:forged' }))).toBe(false);
  });
});
