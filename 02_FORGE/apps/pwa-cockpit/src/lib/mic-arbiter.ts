// Phase 5: cross-cartridge microphone arbitration.
//
// Browsers expose exactly one microphone capture stream per document. If two
// cartridges (Anya STT, interphase getDisplayMedia audio, future kickbox STT
// clients) all call getUserMedia concurrently the user sees conflicting
// permission prompts and only one stream actually works. This module is a
// single-tab in-memory arbiter: callers must `requestMic(holderId, reason)`
// before opening the mic and `releaseMic(holderId)` when done. A second
// caller receives `{ ok: false, currentHolder }` so the UI can surface
// "Microphone in use by {holder}" instead of silently failing.
//
// Persistence to disk is intentionally out of scope for Phase 5 — mic holds
// are per-tab and lose meaning across a process restart anyway. A future
// cross-tab mutex (BroadcastChannel) is documented as a follow-up.

export type MicState = {
  holderId: string | null;
  reason: string | null;
  acquiredAt: number | null;
};

export type MicGrant =
  | { ok: true; revoke: () => void }
  | { ok: false; currentHolder: string | null; reason: string | null };

export type MicSubscriber = (state: MicState) => void;

const state: MicState = { holderId: null, reason: null, acquiredAt: null };
const subscribers = new Set<MicSubscriber>();

function notify() {
  subscribers.forEach((callback) => callback({ ...state }));
}

export function requestMic(holderId: string, reason: string): MicGrant {
  if (state.holderId !== null && state.holderId !== holderId) {
    return { ok: false, currentHolder: state.holderId, reason: state.reason };
  }
  state.holderId = holderId;
  state.reason = reason;
  state.acquiredAt = state.holderId === holderId && state.acquiredAt ? state.acquiredAt : Date.now();
  notify();
  return {
    ok: true,
    revoke: () => releaseMic(holderId),
  };
}

export function releaseMic(holderId: string): void {
  if (state.holderId !== holderId) return;
  state.holderId = null;
  state.reason = null;
  state.acquiredAt = null;
  notify();
}

export function currentHolder(): string | null {
  return state.holderId;
}

export function micState(): MicState {
  return { ...state };
}

export function onMicChange(callback: MicSubscriber): () => void {
  subscribers.add(callback);
  return () => {
    subscribers.delete(callback);
  };
}

// Test/recovery helper: clear all arbiter state. Mirrors clearSeenNonces
// from capabilities.ts.
export function clearMicArbiter(): void {
  state.holderId = null;
  state.reason = null;
  state.acquiredAt = null;
  notify();
}
