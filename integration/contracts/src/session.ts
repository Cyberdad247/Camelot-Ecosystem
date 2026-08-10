// Pure session-view reducer shared by the Anya Console (rendering) and tests.
// Folds SessionEvents from the gateway WebSocket into the state the UI needs:
// avatar state, streaming reply text, live leases, and audit references.
//
// Kickbox owns *rendering*; this reducer only mirrors what the gateway said.
// It never decides policy — a client cannot un-block itself by reducing
// events differently, because execution happens server-side.

import type { CapabilityLease, SessionEvent, SessionUiState } from './types.js';

export interface SessionView {
  uiState: SessionUiState;
  /** Turn currently streaming a reply, if any. */
  streamingTurnId: string | null;
  /** Accumulated reply text per turn. */
  replies: Record<string, string>;
  /** Leases by id, with live status transitions applied. */
  leases: Record<string, CapabilityLease>;
  /** Audit ids seen, newest last. */
  auditIds: string[];
  /** Turns cancelled by barge-in. */
  cancelledTurnIds: string[];
  /** Latest model route (Phase 3): which provider narrated, and whether the
   *  deterministic fallback was served. */
  lastModelRoute: { turnId: string; provider: string; fallback: boolean } | null;
}

export function initialSessionView(): SessionView {
  return {
    uiState: 'idle',
    streamingTurnId: null,
    replies: {},
    leases: {},
    auditIds: [],
    cancelledTurnIds: [],
    lastModelRoute: null,
  };
}

export function reduceSessionEvent(view: SessionView, event: SessionEvent): SessionView {
  switch (event.type) {
    case 'turn.accepted':
      return { ...view, uiState: 'thinking' };

    case 'policy.decision': {
      const uiState: SessionUiState =
        event.decision.effect === 'requires_confirmation' ? 'blocked' : view.uiState;
      return { ...view, uiState };
    }

    case 'lease.issued':
      return {
        ...view,
        leases: { ...view.leases, [event.lease.leaseId]: event.lease },
      };

    case 'lease.consumed': {
      const lease = view.leases[event.leaseId];
      if (!lease) return view;
      return {
        ...view,
        leases: { ...view.leases, [event.leaseId]: { ...lease, status: 'consumed' } },
      };
    }

    case 'lease.revoked': {
      const lease = view.leases[event.leaseId];
      if (!lease) return view;
      const revoked: CapabilityLease = { ...lease, status: 'revoked' };
      delete revoked.token;
      return {
        ...view,
        uiState: view.uiState === 'blocked' ? 'idle' : view.uiState,
        leases: { ...view.leases, [event.leaseId]: revoked },
      };
    }

    case 'reply.chunk': {
      const prior = view.replies[event.turnId] ?? '';
      return {
        ...view,
        uiState: 'speaking',
        streamingTurnId: event.turnId,
        replies: { ...view.replies, [event.turnId]: prior + event.text },
      };
    }

    case 'reply.done':
      return {
        ...view,
        uiState: view.uiState === 'blocked' ? 'blocked' : 'idle',
        streamingTurnId: view.streamingTurnId === event.turnId ? null : view.streamingTurnId,
      };

    case 'turn.cancelled':
      return {
        ...view,
        uiState: 'idle',
        streamingTurnId: view.streamingTurnId === event.turnId ? null : view.streamingTurnId,
        cancelledTurnIds: [...view.cancelledTurnIds, event.turnId],
      };

    case 'audit.appended':
      return { ...view, auditIds: [...view.auditIds, event.auditId] };

    case 'model.route':
      return {
        ...view,
        lastModelRoute: {
          turnId: event.turnId,
          provider: event.provider,
          fallback: event.fallback ?? false,
        },
      };
  }
}
