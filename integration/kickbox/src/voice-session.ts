// Push-to-talk voice session controller (Phase 2). Pure orchestration —
// no DOM — so every guardrail is unit-testable:
//
//   - failed/no transcript          -> nothing is submitted
//   - low confidence                -> user must review before submit
//   - accepted transcript          -> ONLY path is the existing VoiceTurn endpoint
//   - barge-in                      -> playback stops NOW, then the existing
//                                      barge-in event cancels the stream and
//                                      revokes unused leases
//   - mic/STT/TTS failure           -> visible text-only fallback, session useful
//
// Raw audio lives only inside this controller's call stack: captured,
// hashed, transcribed, dropped.

import {
  LOW_CONFIDENCE_THRESHOLD,
  hashAudio,
} from '@camelot/contracts';
import type {
  CapturedAudio,
  PlaybackHandle,
  VoiceProvider,
} from '@camelot/contracts';

export type VoiceUiState =
  | 'voice-idle'
  | 'listening'
  | 'transcribing'
  | 'review'
  | 'voice-error'
  | 'text-only';

export type VoiceNotice =
  | { kind: 'mic-denied'; message: string }
  | { kind: 'stt-failed'; message: string }
  | { kind: 'no-speech'; message: string }
  | { kind: 'low-confidence'; message: string }
  | { kind: 'tts-failed'; message: string };

export interface VoiceSessionCallbacks {
  /** Submit an accepted transcript through the existing turn path. */
  submitTranscript: (transcript: string, meta: { audioSha256: string }) => Promise<{ turnId: string } | void>;
  /** Fire the existing barge-in event for the given turn. */
  bargeIn: (turnId: string) => Promise<void>;
  onState: (state: VoiceUiState) => void;
  onNotice: (notice: VoiceNotice) => void;
  /** Low-confidence transcript offered for review (prefill, don't submit). */
  onReview: (transcript: string, confidence: number) => void;
}

export class VoiceSessionController {
  #provider: VoiceProvider;
  #callbacks: VoiceSessionCallbacks;
  #state: VoiceUiState = 'voice-idle';
  #playback: { handle: PlaybackHandle; turnId: string } | null = null;
  textOnly = false;

  constructor(provider: VoiceProvider, callbacks: VoiceSessionCallbacks) {
    this.#provider = provider;
    this.#callbacks = callbacks;
  }

  get state(): VoiceUiState {
    return this.#state;
  }

  #setState(state: VoiceUiState): void {
    this.#state = state;
    this.#callbacks.onState(state);
  }

  /** Push-to-talk pressed. */
  async pttDown(deviceId?: string): Promise<void> {
    if (this.textOnly) return;
    // Speaking while Anya speaks IS a barge-in — stop her first.
    if (this.#playback) await this.stopSpeaking();
    try {
      await this.#provider.startCapture(deviceId);
      this.#setState('listening');
    } catch (err) {
      this.textOnly = true;
      this.#setState('text-only');
      this.#callbacks.onNotice({
        kind: 'mic-denied',
        message: `Microphone unavailable (${String(err)}). Text mode remains fully functional.`,
      });
    }
  }

  /** Push-to-talk released: transcribe and apply the confidence gate. */
  async pttUp(): Promise<void> {
    if (this.#state !== 'listening') return;
    this.#setState('transcribing');

    let audio: CapturedAudio;
    try {
      audio = await this.#provider.stopCapture();
    } catch (err) {
      this.#setState('voice-error');
      this.#callbacks.onNotice({ kind: 'stt-failed', message: `Capture failed: ${String(err)}` });
      this.#setState('voice-idle');
      return;
    }

    try {
      const result = await this.#provider.transcribe(audio);

      if (result.transcript === null || result.transcript.trim() === '' || result.confidence <= 0) {
        // No usable speech: NOTHING reaches the gateway.
        this.#callbacks.onNotice({
          kind: 'no-speech',
          message: 'No speech detected — nothing was submitted.',
        });
        this.#setState('voice-idle');
        return;
      }

      if (result.confidence < LOW_CONFIDENCE_THRESHOLD) {
        // Low confidence: human review required. NOTHING auto-submits.
        this.#callbacks.onNotice({
          kind: 'low-confidence',
          message: `Low-confidence transcript (${(result.confidence * 100).toFixed(0)}%) — review, then submit or retry.`,
        });
        this.#callbacks.onReview(result.transcript, result.confidence);
        this.#setState('review');
        return;
      }

      // Accepted: hash the audio (its only surviving trace), submit through
      // the one governed path, and let the PCM be garbage-collected.
      const audioSha256 = await hashAudio(audio);
      this.#setState('voice-idle');
      await this.#callbacks.submitTranscript(result.transcript, { audioSha256 });
    } catch (err) {
      // STT failure: no policy request, no tool action, visible notice.
      this.#callbacks.onNotice({ kind: 'stt-failed', message: `Transcription failed: ${String(err)}` });
      this.#setState('voice-idle');
    }
  }

  /** Speak a gateway reply. TTS failure never hides the text. */
  async speakReply(text: string, turnId: string): Promise<void> {
    try {
      const handle = await this.#provider.synthesize(text, { turnId });
      this.#playback = { handle, turnId };
      void handle.done.then(() => {
        if (this.#playback?.turnId === turnId) this.#playback = null;
      });
    } catch (err) {
      this.#callbacks.onNotice({
        kind: 'tts-failed',
        message: `Voice playback unavailable (${String(err)}) — the text response above is complete.`,
      });
    }
  }

  /** Stop-speaking / barge-in: playback halts immediately, THEN the gateway
   *  cancels the stream and revokes unused leases via the existing event. */
  async stopSpeaking(): Promise<void> {
    const playback = this.#playback;
    if (!playback) return;
    this.#playback = null;
    playback.handle.stop(); // immediate, before any network round-trip
    this.#provider.cancel(playback.turnId);
    await this.#callbacks.bargeIn(playback.turnId);
  }

  get speakingTurnId(): string | null {
    return this.#playback?.turnId ?? null;
  }
}
