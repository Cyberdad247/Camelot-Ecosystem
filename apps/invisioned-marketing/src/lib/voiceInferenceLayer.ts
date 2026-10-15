// SPDX-License-Identifier: MIT
// Voice & Sovereign Inference Layer — v10001.00-CYBERTRONIA

export interface VoicePersona {
  id: string;
  name: string;
  title: string;
  avatar: string;
  voiceStyle: string;
  defaultEngine: string;
  cloudBrainUuid: string;
  primaryColor: string;
  vfsPath: string;
  systemPrompt: string;
}

export const SOVEREIGN_PERSONAS: VoicePersona[] = [
  {
    id: 'SIR_HELIO',
    name: 'Sir Helio',
    title: 'Voice OS & 1M Context Navigator',
    avatar: '👁️',
    voiceStyle: 'Gemini Live Duplex (Aoede S2S, 432Hz)',
    defaultEngine: 'Gemini 3.8 Flash / Pro (Live)',
    cloudBrainUuid: '56820318-bb91-451f-aac4-4b46424898cf',
    primaryColor: '#D4AF37',
    vfsPath: 'vfs://worldtree/knights/sir_helio/',
    systemPrompt: 'You are Sir Helio, Sovereign Voice OS Conductor. You deliver low-latency conversational audio, acoustic VAD telemetry, and macroscopic structural insights.'
  },
  {
    id: 'SIR_BORIS',
    name: 'Sir Boris',
    title: 'Crucible Conductor & Lead Architect',
    avatar: '🛡️',
    voiceStyle: 'Crisp Architectural (13-Agent Critique)',
    defaultEngine: 'Claude 3.7 Sonnet / Gemini',
    cloudBrainUuid: 'f7707daa-2d10-4db8-8fda-be4661a27793',
    primaryColor: '#FFD700',
    vfsPath: 'vfs://worldtree/knights/sir_boris/',
    systemPrompt: 'You are Sir Boris, Lead Architect of Camelot-OS. You enforce luxury minimalist brutalism, worktree isolation, and zero-trust Crucible critiques.'
  },
  {
    id: 'LADY_APIS',
    name: 'Lady Apis',
    title: 'Bio-Kinetic Swarm & Context Forager',
    avatar: '🐝',
    voiceStyle: 'Dynamic Swarm Harmonic (NullClaw)',
    defaultEngine: 'Gemini 3.8 Flash',
    cloudBrainUuid: '378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f',
    primaryColor: '#F59E0B',
    vfsPath: 'vfs://worldtree/knights/lady_apis/',
    systemPrompt: 'You are Lady Apis, Conductor of the Bio-Kinetic Swarm. You conduct BASHR research, cellular horde mitosis, and context foraging under 150 tok/pulse.'
  },
  {
    id: 'MERLIN_OMEGA',
    name: 'Merlin Omega',
    title: 'GoT/ToT Deep Reasoning & System 2',
    avatar: '🧙‍♂️',
    voiceStyle: 'Resonant Ancient-Futuristic (Videneptus LaC)',
    defaultEngine: 'Gemini Pro / Opus',
    cloudBrainUuid: 'af927fde-d7eb-42ee-8c79-51b3e78ef39b',
    primaryColor: '#9D4EDD',
    vfsPath: 'vfs://worldtree/knights/merlin_omega/',
    systemPrompt: 'You are Merlin Omega, Archwizard of System 2 Deep Reasoning. You solve complex distributed systems with formal Z3 logic and Graph-of-Thoughts.'
  },
  {
    id: 'SIR_CODEX',
    name: 'Sir Codex',
    title: 'Kinetic Implementer & Z3 Logic Prover',
    avatar: '⚔️',
    voiceStyle: 'Fast Mid-Low Terminal Syntax',
    defaultEngine: 'OpenAI Codex / GPT-5.5',
    cloudBrainUuid: '8c656cfa-a189-409e-a72d-07692a47f17e',
    primaryColor: '#10B981',
    vfsPath: 'vfs://worldtree/knights/sir_codex/',
    systemPrompt: 'You are Sir Codex, kinetic builder and zero-trust logic architect. You build deterministic TypeScript, Rust, and Go with 100% test-first verification.'
  },
  {
    id: 'LADY_LAKISHA',
    name: 'Lady Lakisha',
    title: 'Voice OS Sentinel & Intercom Matrix',
    avatar: '🎙️',
    voiceStyle: 'Smooth Velvet Warmth (WebRTC Intercom)',
    defaultEngine: 'Gemini 2.5 Flash / LiteRT',
    cloudBrainUuid: 'a0a4bfb9-e847-4c38-be39-7aee398f0795',
    primaryColor: '#EC4899',
    vfsPath: 'vfs://worldtree/knights/lady_lakisha/',
    systemPrompt: 'You are Lady Lakisha, Sovereign Intercom Voice OS Sentinel. You manage duplex intercom sessions, acoustic clarity, and luxury aesthetic harmony.'
  }
];

export type InferenceBackend = 'LOCAL_OLLAMA' | 'VPS_OMNIROUTE' | 'GEMINI_LIVE_S2S' | 'CLIPROXY_GATEWAY';

export interface InferenceBackendConfig {
  id: InferenceBackend;
  name: string;
  endpoint: string;
  latencyExpectation: string;
  airGapped: boolean;
  model: string;
}

export const INFERENCE_BACKENDS: Record<InferenceBackend, InferenceBackendConfig> = {
  LOCAL_OLLAMA: {
    id: 'LOCAL_OLLAMA',
    name: 'Local Ollama (Air-Gapped)',
    endpoint: 'http://127.0.0.1:11434/v1',
    latencyExpectation: '< 15ms TTFT',
    airGapped: true,
    model: 'qwen2.5-coder:7b'
  },
  VPS_OMNIROUTE: {
    id: 'VPS_OMNIROUTE',
    name: 'VPS OmniRoute (KVM563)',
    endpoint: 'http://100.110.180.18:20128',
    latencyExpectation: '25-45ms RTT',
    airGapped: false,
    model: 'hermes-3-llama-3.1-8b'
  },
  GEMINI_LIVE_S2S: {
    id: 'GEMINI_LIVE_S2S',
    name: 'Gemini Live Duplex Audio (Aoede)',
    endpoint: 'wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent',
    latencyExpectation: 'Sub-50ms Glass-to-Ear',
    airGapped: false,
    model: 'gemini-2.0-flash-exp'
  },
  CLIPROXY_GATEWAY: {
    id: 'CLIPROXY_GATEWAY',
    name: 'CLIProxy Zero-Cost Gateway',
    endpoint: 'http://127.0.0.1:8080/v1',
    latencyExpectation: '50-90ms',
    airGapped: false,
    model: 'gpt-4o'
  }
};

export interface MeshNodeTelemetry {
  name: string;
  ip: string;
  role: string;
  status: 'ONLINE' | 'LATENT' | 'STANDBY';
  pingMs: number;
}

export const MESH_NODES: MeshNodeTelemetry[] = [
  { name: 'cybertronia', ip: '100.118.224.52', role: 'Primary Windows Orchestrator', status: 'ONLINE', pingMs: 1 },
  { name: 'vashawns-s26-ultra', ip: '100.106.246.126', role: 'Excalibur Command Center (S26)', status: 'ONLINE', pingMs: 18 },
  { name: 'vps-camelot-hub', ip: '100.110.180.18', role: 'Camelot-OS Hub & Bifrost Gateway', status: 'ONLINE', pingMs: 24 },
  { name: 'fothers-camelot', ip: '100.121.48.50', role: 'Windows Sovereign Secondary', status: 'STANDBY', pingMs: 32 },
  { name: 'lakesha', ip: '100.100.155.55', role: 'Lakisha Voice OS Host', status: 'ONLINE', pingMs: 14 }
];
