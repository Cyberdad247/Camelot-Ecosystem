/**
 * KickboxAudioController — Web Audio API gain controller
 * inspired by the Kickbox-audio project's dynamic volume telemetry.
 *
 * Manages a single AudioContext with a master GainNode.
 * Volume is clamped to [0.0, 1.0].
 */
export class KickboxAudioController {
  public ctx: AudioContext | null = null;
  private gainNode: GainNode | null = null;
  private volume: number = 1.0;

  /** Initialise the AudioContext and connect the master gain node. */
  public init() {
    const AudioContextClass =
      (globalThis as any).AudioContext || (globalThis as any).webkitAudioContext;
    this.ctx = new AudioContextClass();
    this.gainNode = this.ctx.createGain();
    this.gainNode.gain.setValueAtTime(this.volume, this.ctx.currentTime);
    this.gainNode.connect(this.ctx.destination);
  }

  /** Set the master volume (clamped 0.0–1.0). */
  public setVolume(val: number) {
    this.volume = Math.max(0, Math.min(1, val));
    if (this.gainNode && this.ctx) {
      this.gainNode.gain.setValueAtTime(this.volume, this.ctx.currentTime);
    }
  }

  /** Return the current master volume. */
  public getVolume(): number {
    return this.volume;
  }

  /** Tear down the AudioContext (call on component unmount). */
  public dispose() {
    if (this.gainNode) {
      this.gainNode.disconnect();
      this.gainNode = null;
    }
    if (this.ctx && this.ctx.state !== 'closed') {
      this.ctx.close();
      this.ctx = null;
    }
  }
}
