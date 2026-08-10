// Voice provider contract (Phase 2). Hermes remains an ADAPTER (ADR-001):
// a VoiceProvider may capture, transcribe, and speak — it has no access to
// skills, leases, tools, or the gateway. Transcripts enter Camelot only
// through the existing VoiceTurn endpoint, after the confidence gate.

export interface CapturedAudio {
  /** PCM16 mono samples. Raw audio is ephemeral: kept in memory, hashed,
   *  then dropped. It never reaches the gateway or the audit log. */
  pcm16: Int16Array;
  sampleRate: number;
  durationMs: number;
}

export interface TranscriptResult {
  /** null = no usable speech (silence, decode failure). Never submit these. */
  transcript: string | null;
  /** 0..1. Below LOW_CONFIDENCE_THRESHOLD the user must review before submit. */
  confidence: number;
  provider: string;
}

export interface SynthesisDirectives {
  /** Turn the speech belongs to — lets barge-in cancel the right playback. */
  turnId: string;
  voice?: string;
  rate?: number;
}

export interface PlaybackHandle {
  /** Resolves when playback finishes or is stopped. */
  done: Promise<void>;
  /** Stop output immediately (barge-in path). Idempotent. */
  stop: () => void;
}

export interface VoiceHealth {
  ok: boolean;
  provider: string;
  stt: string;
  tts: string;
  detail?: string;
}

/** Transcripts below this confidence require explicit user review. */
export const LOW_CONFIDENCE_THRESHOLD = 0.75;

export interface VoiceProvider {
  startCapture(deviceId?: string): Promise<void>;
  stopCapture(): Promise<CapturedAudio>;
  transcribe(audio: CapturedAudio): Promise<TranscriptResult>;
  synthesize(text: string, directives: SynthesisDirectives): Promise<PlaybackHandle>;
  /** Cancel any in-flight transcription/synthesis for a turn. */
  cancel(turnId: string): void;
  health(): Promise<VoiceHealth>;
}

// ── Mock provider — THE default for tests and deterministic demos ────────

export interface MockScriptEntry {
  transcript: string | null;
  confidence: number;
}

export interface MockVoiceProviderOptions {
  /** Utterances returned by successive transcribe() calls (cycled). */
  script?: MockScriptEntry[];
  failCapture?: boolean;
  failTranscribe?: boolean;
  failSynthesize?: boolean;
  sampleRate?: number;
}

export class MockVoiceProvider implements VoiceProvider {
  readonly spoken: Array<{ text: string; turnId: string }> = [];
  readonly cancelledTurns: string[] = [];
  readonly stoppedPlaybacks: string[] = [];
  #script: MockScriptEntry[];
  #scriptIndex = 0;
  #options: MockVoiceProviderOptions;
  #capturing = false;

  constructor(options: MockVoiceProviderOptions = {}) {
    this.#options = options;
    this.#script = options.script ?? [
      { transcript: 'read staging status', confidence: 0.92 },
      { transcript: 'prepare a deployment review', confidence: 0.92 },
      { transcript: 'create a change request to scale the api tier', confidence: 0.92 },
    ];
  }

  async startCapture(): Promise<void> {
    if (this.#options.failCapture) {
      throw new Error('microphone permission denied');
    }
    this.#capturing = true;
  }

  async stopCapture(): Promise<CapturedAudio> {
    if (!this.#capturing) throw new Error('capture was not active');
    this.#capturing = false;
    const sampleRate = this.#options.sampleRate ?? 16000;
    // Deterministic 250ms ramp — enough to hash reproducibly.
    const pcm16 = new Int16Array(sampleRate / 4);
    for (let i = 0; i < pcm16.length; i++) pcm16[i] = (i % 1000) - 500;
    return { pcm16, sampleRate, durationMs: 250 };
  }

  async transcribe(_audio: CapturedAudio): Promise<TranscriptResult> {
    if (this.#options.failTranscribe) {
      throw new Error('stt backend unavailable');
    }
    const entry = this.#script[this.#scriptIndex % this.#script.length]!;
    this.#scriptIndex += 1;
    return { ...entry, provider: 'mock' };
  }

  async synthesize(text: string, directives: SynthesisDirectives): Promise<PlaybackHandle> {
    if (this.#options.failSynthesize) {
      throw new Error('tts backend unavailable');
    }
    this.spoken.push({ text, turnId: directives.turnId });
    let resolveDone!: () => void;
    const done = new Promise<void>((resolve) => {
      resolveDone = resolve;
    });
    const stop = () => {
      this.stoppedPlaybacks.push(directives.turnId);
      resolveDone();
    };
    // Mock playback "finishes" only when stopped or after a macrotask tick,
    // so tests can interrupt it deterministically.
    setTimeout(resolveDone, 5);
    return { done, stop };
  }

  cancel(turnId: string): void {
    this.cancelledTurns.push(turnId);
  }

  async health(): Promise<VoiceHealth> {
    return { ok: true, provider: 'mock', stt: 'fixture', tts: 'fixture' };
  }
}

/** SHA-256 of the raw PCM bytes — the only trace of audio that persists. */
export async function hashAudio(audio: CapturedAudio): Promise<string> {
  // Copy into a fresh ArrayBuffer-backed view (satisfies BufferSource even
  // when the source PCM lives in a SharedArrayBuffer).
  const bytes = new Uint8Array(audio.pcm16.byteLength);
  bytes.set(new Uint8Array(audio.pcm16.buffer, audio.pcm16.byteOffset, audio.pcm16.byteLength));
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, '0')).join('');
}
