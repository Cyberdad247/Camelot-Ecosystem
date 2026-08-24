// Browser VoiceProvider backed by the native Hermes adapter service.
// Capture: getUserMedia -> AudioContext -> PCM16 @16kHz (in memory only).
// STT: POST /v1/stt to Hermes. TTS: browser speechSynthesis when available
// (offline, no model process), otherwise Hermes /v1/tts WAV playback.
// Hermes never sees the gateway; this provider never sees a tool.

import type {
  CapturedAudio,
  PlaybackHandle,
  SynthesisDirectives,
  TranscriptResult,
  VoiceHealth,
  VoiceProvider,
} from '@camelot/contracts';

const TARGET_SAMPLE_RATE = 16000;

export class HermesVoiceProvider implements VoiceProvider {
  #baseUrl: string;
  #stream: MediaStream | null = null;
  #audioContext: AudioContext | null = null;
  #chunks: Float32Array[] = [];
  #sourceSampleRate = TARGET_SAMPLE_RATE;
  #activeAudio: HTMLAudioElement | null = null;

  constructor(baseUrl: string) {
    this.#baseUrl = baseUrl.replace(/\/+$/, '');
  }

  async startCapture(deviceId?: string): Promise<void> {
    const constraints: MediaStreamConstraints = {
      audio: deviceId ? { deviceId: { exact: deviceId } } : true,
    };
    this.#stream = await navigator.mediaDevices.getUserMedia(constraints);
    this.#audioContext = new AudioContext();
    this.#sourceSampleRate = this.#audioContext.sampleRate;
    this.#chunks = [];
    const source = this.#audioContext.createMediaStreamSource(this.#stream);
    const processor = this.#audioContext.createScriptProcessor(4096, 1, 1);
    processor.onaudioprocess = (e) => {
      this.#chunks.push(new Float32Array(e.inputBuffer.getChannelData(0)));
    };
    source.connect(processor);
    processor.connect(this.#audioContext.destination);
  }

  async stopCapture(): Promise<CapturedAudio> {
    const chunks = this.#chunks;
    this.#chunks = [];
    for (const track of this.#stream?.getTracks() ?? []) track.stop();
    this.#stream = null;
    if (this.#audioContext && this.#audioContext.state !== 'closed') {
      await this.#audioContext.close();
    }
    this.#audioContext = null;

    const total = chunks.reduce((n, c) => n + c.length, 0);
    const joined = new Float32Array(total);
    let offset = 0;
    for (const c of chunks) {
      joined.set(c, offset);
      offset += c.length;
    }
    const ratio = this.#sourceSampleRate / TARGET_SAMPLE_RATE;
    const outLength = Math.max(1, Math.floor(joined.length / ratio));
    const pcm16 = new Int16Array(outLength);
    for (let i = 0; i < outLength; i++) {
      const sample = joined[Math.floor(i * ratio)] ?? 0;
      pcm16[i] = Math.max(-32768, Math.min(32767, Math.round(sample * 32767)));
    }
    return {
      pcm16,
      sampleRate: TARGET_SAMPLE_RATE,
      durationMs: Math.round((outLength / TARGET_SAMPLE_RATE) * 1000),
    };
  }

  async transcribe(audio: CapturedAudio): Promise<TranscriptResult> {
    const bytes = new Uint8Array(audio.pcm16.buffer, audio.pcm16.byteOffset, audio.pcm16.byteLength);
    let binary = '';
    for (let i = 0; i < bytes.length; i += 0x8000) {
      binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    }
    const res = await fetch(`${this.#baseUrl}/v1/stt`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ sampleRate: audio.sampleRate, pcm16: btoa(binary) }),
    });
    if (!res.ok) throw new Error(`hermes stt HTTP ${res.status}`);
    const body = (await res.json()) as { transcript: string | null; confidence: number; engine: string };
    return { transcript: body.transcript, confidence: body.confidence, provider: `hermes/${body.engine}` };
  }

  async synthesize(text: string, directives: SynthesisDirectives): Promise<PlaybackHandle> {
    if (typeof speechSynthesis !== 'undefined' && speechSynthesis.getVoices !== undefined) {
      return this.#speakLocally(text, directives);
    }
    return this.#speakViaHermes(text);
  }

  #speakLocally(text: string, directives: SynthesisDirectives): PlaybackHandle {
    const utterance = new SpeechSynthesisUtterance(text);
    if (directives.rate) utterance.rate = directives.rate;
    let resolveDone!: () => void;
    const done = new Promise<void>((resolve) => {
      resolveDone = resolve;
    });
    utterance.onend = () => resolveDone();
    utterance.onerror = () => resolveDone();
    speechSynthesis.speak(utterance);
    return {
      done,
      stop: () => {
        speechSynthesis.cancel();
        resolveDone();
      },
    };
  }

  async #speakViaHermes(text: string): Promise<PlaybackHandle> {
    const res = await fetch(`${this.#baseUrl}/v1/tts`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error(`hermes tts HTTP ${res.status}`);
    const url = URL.createObjectURL(await res.blob());
    const audio = new Audio(url);
    this.#activeAudio = audio;
    let resolveDone!: () => void;
    const done = new Promise<void>((resolve) => {
      resolveDone = resolve;
    });
    const cleanup = () => {
      URL.revokeObjectURL(url);
      if (this.#activeAudio === audio) this.#activeAudio = null;
      resolveDone();
    };
    audio.onended = cleanup;
    audio.onerror = cleanup;
    await audio.play();
    return {
      done,
      stop: () => {
        audio.pause();
        cleanup();
      },
    };
  }

  cancel(_turnId: string): void {
    if (typeof speechSynthesis !== 'undefined') speechSynthesis.cancel();
    this.#activeAudio?.pause();
    this.#activeAudio = null;
  }

  async health(): Promise<VoiceHealth> {
    try {
      const res = await fetch(`${this.#baseUrl}/healthz`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const body = (await res.json()) as { stt: string; tts: string };
      return { ok: true, provider: 'hermes', stt: body.stt, tts: body.tts };
    } catch (err) {
      return { ok: false, provider: 'hermes', stt: 'unreachable', tts: 'unreachable', detail: String(err) };
    }
  }
}
