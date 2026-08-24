// T4 (client half): barge-in cancels response streaming and revokes the
// unused lease — as observed by the session reducer the Console renders from.

import { describe, expect, it } from 'vitest';
import {
  initialSessionView,
  reduceSessionEvent,
} from '../src/index.js';
import type { CapabilityLease, SessionEvent, SessionView } from '../src/index.js';

const lease: CapabilityLease = {
  leaseId: 'lease-1',
  sessionId: 'sess-anya-demo-001',
  turnId: 'turn-0002',
  capability: 'skill:change_request.create',
  status: 'approved',
  issuedAt: '2026-08-07T00:00:00Z',
  expiresAt: '2026-08-07T00:00:30Z',
  singleUse: true,
  token: 'signed-opaque-token',
};

function reduceAll(events: SessionEvent[], from: SessionView = initialSessionView()): SessionView {
  return events.reduce(reduceSessionEvent, from);
}

describe('barge-in over the session event stream', () => {
  it('streaming reply puts the avatar in "speaking" and accumulates text', () => {
    const view = reduceAll([
      { type: 'turn.accepted', turnId: 'turn-0002' },
      { type: 'reply.chunk', turnId: 'turn-0002', seq: 0, text: 'Drafting ' },
      { type: 'reply.chunk', turnId: 'turn-0002', seq: 1, text: 'the review…' },
    ]);
    expect(view.uiState).toBe('speaking');
    expect(view.streamingTurnId).toBe('turn-0002');
    expect(view.replies['turn-0002']).toBe('Drafting the review…');
  });

  it('barge-in cancels the stream and revokes the unused lease', () => {
    const mid = reduceAll([
      { type: 'turn.accepted', turnId: 'turn-0002' },
      { type: 'lease.issued', lease },
      { type: 'reply.chunk', turnId: 'turn-0002', seq: 0, text: 'Working…' },
    ]);
    expect(mid.uiState).toBe('speaking');
    expect(mid.leases['lease-1']?.status).toBe('approved');

    const after = reduceAll(
      [
        { type: 'turn.cancelled', turnId: 'turn-0002', reason: 'barge-in' },
        { type: 'lease.revoked', leaseId: 'lease-1', reason: 'barge-in' },
      ],
      mid,
    );
    expect(after.uiState).toBe('idle');
    expect(after.streamingTurnId).toBeNull();
    expect(after.cancelledTurnIds).toContain('turn-0002');
    expect(after.leases['lease-1']?.status).toBe('revoked');
    // The signed token is wiped the moment the lease dies.
    expect(after.leases['lease-1']?.token).toBeUndefined();
  });

  it('a consumed lease is not affected by later revocation of others', () => {
    const view = reduceAll([
      { type: 'lease.issued', lease },
      { type: 'lease.consumed', leaseId: 'lease-1' },
      { type: 'lease.revoked', leaseId: 'lease-does-not-exist', reason: 'noop' },
    ]);
    expect(view.leases['lease-1']?.status).toBe('consumed');
  });

  it('requires_confirmation blocks the session until the lease resolves', () => {
    const blocked = reduceAll([
      { type: 'turn.accepted', turnId: 'turn-0003' },
      {
        type: 'policy.decision',
        turnId: 'turn-0003',
        decision: {
          decisionId: 'dec-3',
          effect: 'requires_confirmation',
          skillId: 'change_request.create',
          tier: 3,
          reason: 'tier-3 skills require human confirmation',
          policyVersion: 'v1',
          decidedAt: '2026-08-07T00:00:00Z',
        },
      },
    ]);
    expect(blocked.uiState).toBe('blocked');

    const denied = reduceAll(
      [
        { type: 'lease.issued', lease: { ...lease, leaseId: 'lease-2', status: 'pending' } },
        { type: 'lease.revoked', leaseId: 'lease-2', reason: 'denied by user' },
      ],
      blocked,
    );
    expect(denied.uiState).toBe('idle');
  });
});
