export type VoiceRuntimeState =
  | "idle"
  | "requesting"
  | "listening"
  | "detecting"
  | "transcribing"
  | "speaking"
  | "interrupted"
  | "unavailable";

export type VoiceTransportMode = "shared-ring" | "message-port";

export type VoiceFrame = {
  sessionId: string;
  sequence: number;
  timestampMs: number;
  sampleRate: 16000;
  channels: 1;
  sampleCount: number;
  discontinuity: boolean;
  speech: boolean;
  rms: number;
  samples: Int16Array;
};

export type VoiceUtterance = {
  sessionId: string;
  startedAtMs: number;
  endedAtMs: number;
  sampleRate: 16000;
  samples: Int16Array;
  truncated: boolean;
};

export type VoiceRuntimeMetrics = {
  state: VoiceRuntimeState;
  transport: VoiceTransportMode | null;
  frames: number;
  droppedSamples: number;
  utterances: number;
  lastRms: number;
};

export type ResourceGateResult = { ok: true } | { ok: false; reason: string };

export type VoiceFirstRuntimeOptions = {
  holderId: string;
  reason?: string;
  workletUrl?: string;
  vadThreshold?: number;
  minSpeechMs?: number;
  silenceMs?: number;
  maxUtteranceMs?: number;
  resourceGate?: () => ResourceGateResult;
  getUserMedia?: (constraints: MediaStreamConstraints) => Promise<MediaStream>;
  createAudioContext?: () => AudioContext;
  onState?: (state: VoiceRuntimeState, detail?: string) => void;
  onFrame?: (frame: VoiceFrame) => void | Promise<void>;
  onUtterance?: (utterance: VoiceUtterance) => void | Promise<void>;
  onMetrics?: (metrics: VoiceRuntimeMetrics) => void;
};
