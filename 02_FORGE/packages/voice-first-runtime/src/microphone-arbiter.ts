export type MicrophoneLeaseState = {
  holderId: string | null;
  reason: string | null;
  acquiredAt: number | null;
};

export type MicrophoneLease =
  | { ok: true; release: () => void }
  | { ok: false; currentHolder: string; reason: string | null };

type Subscriber = (state: MicrophoneLeaseState) => void;

export class MicrophoneArbiter {
  private state: MicrophoneLeaseState = { holderId: null, reason: null, acquiredAt: null };
  private readonly subscribers = new Set<Subscriber>();

  acquire(holderId: string, reason: string): MicrophoneLease {
    if (!holderId.trim()) throw new Error("Microphone holderId is required.");
    if (this.state.holderId && this.state.holderId !== holderId) {
      return { ok: false, currentHolder: this.state.holderId, reason: this.state.reason };
    }
    if (!this.state.holderId) {
      this.state = { holderId, reason, acquiredAt: Date.now() };
      this.notify();
    }
    return { ok: true, release: () => this.release(holderId) };
  }

  release(holderId: string): void {
    if (this.state.holderId !== holderId) return;
    this.state = { holderId: null, reason: null, acquiredAt: null };
    this.notify();
  }

  snapshot(): MicrophoneLeaseState {
    return { ...this.state };
  }

  subscribe(callback: Subscriber): () => void {
    this.subscribers.add(callback);
    callback(this.snapshot());
    return () => this.subscribers.delete(callback);
  }

  clear(): void {
    this.state = { holderId: null, reason: null, acquiredAt: null };
    this.notify();
  }

  private notify(): void {
    const snapshot = this.snapshot();
    this.subscribers.forEach((callback) => callback(snapshot));
  }
}

export const microphoneArbiter = new MicrophoneArbiter();
