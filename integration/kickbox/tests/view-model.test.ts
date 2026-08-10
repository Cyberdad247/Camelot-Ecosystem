import { describe, expect, it } from 'vitest';
import { initialSessionView, reduceSessionEvent } from '@camelot/contracts';
import type { CapabilityLease, SessionView } from '@camelot/contracts';
import {
  approvalVisible,
  avatarBadge,
  bargeInAvailable,
  decisionCardModel,
  pendingLease,
} from '../src/view-model.js';

const lease: CapabilityLease = {
  leaseId: 'lease-9',
  sessionId: 's',
  turnId: 'turn-0001',
  capability: 'skill:change_request.create',
  status: 'pending',
  issuedAt: '2026-08-07T00:00:00Z',
  expiresAt: '2026-08-07T00:00:30Z',
  singleUse: true,
};

describe('Anya Console view-model', () => {
  it('maps session states to avatar badges', () => {
    const base = initialSessionView();
    expect(avatarBadge(base).cssClass).toBe('state-idle');
    expect(avatarBadge({ ...base, uiState: 'thinking' }).cssClass).toBe('state-thinking');
    expect(avatarBadge({ ...base, uiState: 'speaking' }).cssClass).toBe('state-speaking');
    expect(avatarBadge({ ...base, uiState: 'blocked' }).cssClass).toBe('state-blocked');
  });

  it('shows the approval control only while a lease is pending', () => {
    let view: SessionView = initialSessionView();
    expect(approvalVisible(view)).toBe(false);

    view = reduceSessionEvent(view, { type: 'lease.issued', lease });
    expect(approvalVisible(view)).toBe(true);
    expect(pendingLease(view)?.leaseId).toBe('lease-9');

    const revoked = reduceSessionEvent(view, {
      type: 'lease.revoked',
      leaseId: 'lease-9',
      reason: 'denied',
    });
    expect(approvalVisible(revoked)).toBe(false);

    const consumed = reduceSessionEvent(view, { type: 'lease.consumed', leaseId: 'lease-9' });
    expect(approvalVisible(consumed)).toBe(false);
  });

  it('offers barge-in only during active streaming', () => {
    let view: SessionView = initialSessionView();
    expect(bargeInAvailable(view)).toBe(false);
    view = reduceSessionEvent(view, { type: 'reply.chunk', turnId: 't', seq: 0, text: 'hi' });
    expect(bargeInAvailable(view)).toBe(true);
    view = reduceSessionEvent(view, { type: 'turn.cancelled', turnId: 't', reason: 'barge-in' });
    expect(bargeInAvailable(view)).toBe(false);
  });

  it('renders decision effects with the right emphasis', () => {
    expect(decisionCardModel(null).effectClass).toBe('effect-none');
    const model = decisionCardModel({
      decisionId: 'dec-1',
      effect: 'requires_confirmation',
      skillId: 'change_request.create',
      tier: 3,
      reason: 'tier-3 skills require human confirmation',
      policyVersion: 'v1',
      decidedAt: '2026-08-07T00:00:00Z',
    });
    expect(model.effectLabel).toBe('NEEDS CONFIRMATION');
    expect(model.effectClass).toBe('effect-confirm');
    expect(model.skillLine).toContain('tier 3');
  });
});
