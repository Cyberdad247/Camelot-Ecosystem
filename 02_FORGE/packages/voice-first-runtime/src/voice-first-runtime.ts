import { microphoneArbiter, type MicrophoneLease } from "./microphone-arbiter";
import { SharedPcmRing, sharedPcmAvailable } from "./shared-pcm-ring";
import type {
  VoiceFirstRuntimeOptions,
  VoiceFrame,
  VoiceRuntimeMetrics,
  VoiceRuntimeState,
  VoiceTransportMode,
  VoiceUtterance,
} from "./types";

type WorkletFrameMessage = {
  type: "frame";
  sequence: number;
  timestampMs: number;
  sampleCount: number;
  discontinuity: boolean;
  speech: boolean;
  rms: number;
  samples?: ArrayBuffer;
};

const TARGET_SAMPLE_RATE = 16_000 as const;
const MAX_FRAME_SAMPLES = 1_600;

function sessionId(): string {
  const bytes = new Uint8Array(12);
  crypto.getRandomValues(bytes);
  return `vfc-${Array.from(bytes, (value) => value.toString(16).padStart(2, "0")).join("")}`;
}

function combineFrames(frames: Int16Array[], maxSamples: number): { samples: Int16Array; truncated: boolean } {
  const total = frames.reduce((sum, frame) => sum + frame.length, 0);
  const count = Math.min(total, maxSamples);
  const output = new Int16Array(count);
  let offset = 0;
  for (const frame of frames) {
    if (offset >= count) break;
    const slice = frame.subarray(0, count - offset);
    output.set(slice, offset);
    offset += slice.length;
  }
  return { samples: output, truncated: total > count };
}

export class VoiceFirstRuntime {
  private state: VoiceRuntimeState = "idle";
  private transport: VoiceTransportMode | null = null;
  private stream: MediaStream | null = null;
  private context: AudioContext | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private node: AudioWorkletNode | null = null;
  private sink: GainNode | null = null;
  private ring: SharedPcmRing | null = null;
  private lease: MicrophoneLease | null = null;
  private readonly id = sessionId();
  private frames = 0;
  private utterances = 0;
  private lastDropped = 0;
  private lastRms = 0;
  private utteranceFrames: Int16Array[] = [];
  private speechStartedAt: number | null = null;
  private lastSpeechAt: number | null = null;
  private operation = 0;

  constructor(private readonly options: VoiceFirstRuntimeOptions) {}

  snapshot(): VoiceRuntimeMetrics {
    return {
      state: this.state,
      transport: this.transport,
      frames: this.frames,
      droppedSamples: this.lastDropped,
      utterances: this.utterances,
      lastRms: this.lastRms,
    };
  }

  async start(): Promise<void> {
    if (this.state !== "idle" && this.state !== "unavailable") return;
    const gate = this.options.resourceGate?.();
    if (gate && !gate.ok) {
      this.setState("unavailable", gate.reason);
      throw new Error(gate.reason);
    }

    const lease = microphoneArbiter.acquire(this.options.holderId, this.options.reason ?? "voice capture");
    if (!lease.ok) {
      const detail = `Microphone is in use by ${lease.currentHolder}.`;
      this.setState("unavailable", detail);
      throw new Error(detail);
    }
    this.lease = lease;
    this.setState("requesting");
    const operation = ++this.operation;

    try {
      const getUserMedia = this.options.getUserMedia
        ?? ((constraints: MediaStreamConstraints) => navigator.mediaDevices.getUserMedia(constraints));
      this.stream = await getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
        },
        video: false,
      });
      if (operation !== this.operation) {
        this.stream.getTracks().forEach((track) => track.stop());
        this.stream = null;
        return;
      }

      const createContext = this.options.createAudioContext
        ?? (() => new AudioContext({ latencyHint: "interactive" }));
      this.context = createContext();
      await this.context.audioWorklet.addModule(this.options.workletUrl ?? "/voice-capture.worklet.js");
      if (this.context.state === "suspended") await this.context.resume();

      this.transport = sharedPcmAvailable() ? "shared-ring" : "message-port";
      this.ring = this.transport === "shared-ring" ? new SharedPcmRing() : null;
      this.node = new AudioWorkletNode(this.context, "camelot-voice-capture", {
        numberOfInputs: 1,
        numberOfOutputs: 1,
        outputChannelCount: [1],
        processorOptions: {
          targetSampleRate: TARGET_SAMPLE_RATE,
          frameSamples: MAX_FRAME_SAMPLES,
          vadThreshold: this.options.vadThreshold ?? 0.01,
          ring: this.ring?.handles ?? null,
        },
      });
      this.node.port.onmessage = (event: MessageEvent<WorkletFrameMessage>) => this.handleWorkletMessage(event.data);
      this.source = this.context.createMediaStreamSource(this.stream);
      this.sink = this.context.createGain();
      this.sink.gain.value = 0;
      this.source.connect(this.node);
      this.node.connect(this.sink);
      this.sink.connect(this.context.destination);
      this.setState("listening");
    } catch (error) {
      await this.stop("unavailable");
      const detail = error instanceof Error ? error.message : "Voice capture could not start.";
      this.setState("unavailable", detail);
      throw error;
    }
  }

  interrupt(): void {
    this.resetUtterance();
    this.setState("interrupted");
    if (this.stream) queueMicrotask(() => this.setState("listening"));
  }

  async stop(finalState: VoiceRuntimeState = "idle"): Promise<void> {
    this.operation += 1;
    this.resetUtterance();
    this.node?.port.postMessage({ type: "stop" });
    if (this.node) this.node.port.onmessage = null;
    this.source?.disconnect();
    this.node?.disconnect();
    this.sink?.disconnect();
    this.stream?.getTracks().forEach((track) => track.stop());
    this.ring?.close();
    const context = this.context;
    this.source = null;
    this.node = null;
    this.sink = null;
    this.stream = null;
    this.ring = null;
    this.transport = null;
    if (this.lease?.ok) this.lease.release();
    this.lease = null;
    this.context = null;
    if (context && context.state !== "closed") await context.close().catch(() => undefined);
    this.setState(finalState);
  }

  private handleWorkletMessage(message: WorkletFrameMessage): void {
    if (message.type !== "frame" || message.sampleCount < 1 || message.sampleCount > MAX_FRAME_SAMPLES) return;
    const samples = this.ring
      ? this.ring.read(message.sampleCount)
      : message.samples instanceof ArrayBuffer
        ? new Int16Array(message.samples)
        : new Int16Array();
    if (!samples.length) return;

    const dropped = this.ring?.droppedSamples() ?? 0;
    const discontinuity = message.discontinuity || dropped > this.lastDropped || samples.length !== message.sampleCount;
    this.lastDropped = dropped;
    this.frames += 1;
    this.lastRms = message.rms;
    const frame: VoiceFrame = {
      sessionId: this.id,
      sequence: message.sequence,
      timestampMs: message.timestampMs,
      sampleRate: TARGET_SAMPLE_RATE,
      channels: 1,
      sampleCount: samples.length,
      discontinuity,
      speech: message.speech,
      rms: message.rms,
      samples,
    };
    void this.options.onFrame?.(frame);
    this.updateUtterance(frame);
    this.emitMetrics();
  }

  private updateUtterance(frame: VoiceFrame): void {
    const minSpeechMs = this.options.minSpeechMs ?? 200;
    const silenceMs = this.options.silenceMs ?? 800;
    const maxUtteranceMs = this.options.maxUtteranceMs ?? 30_000;
    if (frame.speech) {
      if (this.speechStartedAt === null) {
        this.speechStartedAt = frame.timestampMs;
        this.setState("detecting");
      }
      this.lastSpeechAt = frame.timestampMs;
    }
    if (this.speechStartedAt !== null) this.utteranceFrames.push(frame.samples.slice());

    const elapsed = this.speechStartedAt === null ? 0 : frame.timestampMs - this.speechStartedAt;
    const silence = this.lastSpeechAt === null ? 0 : frame.timestampMs - this.lastSpeechAt;
    if (this.speechStartedAt !== null && elapsed >= minSpeechMs && this.state === "detecting") {
      this.setState("listening");
    }
    if (this.speechStartedAt !== null && (silence >= silenceMs || elapsed >= maxUtteranceMs)) {
      const startedAtMs = this.speechStartedAt;
      const combined = combineFrames(this.utteranceFrames, Math.round((maxUtteranceMs / 1000) * TARGET_SAMPLE_RATE));
      const utterance: VoiceUtterance = {
        sessionId: this.id,
        startedAtMs,
        endedAtMs: frame.timestampMs,
        sampleRate: TARGET_SAMPLE_RATE,
        samples: combined.samples,
        truncated: combined.truncated || elapsed >= maxUtteranceMs,
      };
      this.utterances += 1;
      this.resetUtterance();
      void this.options.onUtterance?.(utterance);
      this.setState("transcribing");
      queueMicrotask(() => this.stream && this.setState("listening"));
    }
  }

  private resetUtterance(): void {
    this.utteranceFrames = [];
    this.speechStartedAt = null;
    this.lastSpeechAt = null;
  }

  private setState(state: VoiceRuntimeState, detail?: string): void {
    this.state = state;
    this.options.onState?.(state, detail);
    this.emitMetrics();
  }

  private emitMetrics(): void {
    this.options.onMetrics?.(this.snapshot());
  }
}
