import {
  microphoneArbiter,
  type MicrophoneLeaseState,
} from "@camelot/voice-first-runtime";

export type MicState = MicrophoneLeaseState;
export type MicGrant =
  | { ok: true; revoke: () => void }
  | { ok: false; currentHolder: string | null; reason: string | null };
export type MicSubscriber = (state: MicState) => void;

export function requestMic(holderId: string, reason: string): MicGrant {
  const lease = microphoneArbiter.acquire(holderId, reason);
  if (!lease.ok) {
    return { ok: false, currentHolder: lease.currentHolder, reason: lease.reason };
  }
  return { ok: true, revoke: lease.release };
}

export function releaseMic(holderId: string): void {
  microphoneArbiter.release(holderId);
}

export function currentHolder(): string | null {
  return microphoneArbiter.snapshot().holderId;
}

export function micState(): MicState {
  return microphoneArbiter.snapshot();
}

export function onMicChange(callback: MicSubscriber): () => void {
  return microphoneArbiter.subscribe(callback);
}

export function clearMicArbiter(): void {
  microphoneArbiter.clear();
}
