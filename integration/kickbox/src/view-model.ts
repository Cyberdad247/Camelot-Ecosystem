// Pure view-model helpers for the Anya Console. Kept free of DOM access so
// they are unit-testable and portable into the real Kickbox PWA later.

import type { CapabilityLease, PolicyDecision, SessionView } from '@camelot/contracts';

export interface AvatarBadge {
  label: string;
  cssClass: 'state-idle' | 'state-thinking' | 'state-speaking' | 'state-blocked';
}

export function avatarBadge(view: SessionView): AvatarBadge {
  switch (view.uiState) {
    case 'thinking':
      return { label: 'Thinking…', cssClass: 'state-thinking' };
    case 'speaking':
      return { label: 'Speaking', cssClass: 'state-speaking' };
    case 'blocked':
      return { label: 'Awaiting approval', cssClass: 'state-blocked' };
    default:
      return { label: 'Idle', cssClass: 'state-idle' };
  }
}

/** The lease the approval control should offer, if any: pending and current. */
export function pendingLease(view: SessionView): CapabilityLease | null {
  const pending = Object.values(view.leases).filter((l) => l.status === 'pending');
  return pending.length > 0 ? (pending[pending.length - 1] ?? null) : null;
}

/** The approval control renders only while a pending lease exists. */
export function approvalVisible(view: SessionView): boolean {
  return pendingLease(view) !== null;
}

/** Barge-in is offered only while a reply is actively streaming. */
export function bargeInAvailable(view: SessionView): boolean {
  return view.streamingTurnId !== null;
}

export function decisionCardModel(decision: PolicyDecision | null): {
  effectLabel: string;
  effectClass: 'effect-allow' | 'effect-deny' | 'effect-confirm' | 'effect-none';
  skillLine: string;
  reason: string;
} {
  if (!decision) {
    return { effectLabel: 'No decision yet', effectClass: 'effect-none', skillLine: '—', reason: '' };
  }
  const effectLabel =
    decision.effect === 'allow'
      ? 'ALLOWED'
      : decision.effect === 'deny'
        ? 'DENIED'
        : 'NEEDS CONFIRMATION';
  const effectClass =
    decision.effect === 'allow'
      ? 'effect-allow'
      : decision.effect === 'deny'
        ? 'effect-deny'
        : 'effect-confirm';
  return {
    effectLabel,
    effectClass,
    skillLine: `${decision.skillId} · tier ${decision.tier} · policy ${decision.policyVersion}`,
    reason: decision.reason,
  };
}
