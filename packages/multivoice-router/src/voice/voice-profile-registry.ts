export type VoiceEngine = 'vibevoice_realtime' | 'kokoro_onnx' | 'piper' | 'gemini_live' | 'suno' | 'udio' | 'notebooklm_audio' | 'stub';
export type VoiceMode = 'single' | 'council' | 'podcast' | 'automation';

export interface VoiceProfile {
  speakerId: string;
  knightId: string;
  displayName: string;
  engine: VoiceEngine;
  style: string;
  allowedModes: VoiceMode[];
  safetyNotes: string[];
}

export const VOICE_PROFILES: VoiceProfile[] = [
  {
    speakerId: 'anya_host',
    knightId: 'anya_omega',
    displayName: 'Anya Ω',
    engine: 'gemini_live',
    style: 'fast, warm, street-smart operator voice; clear command framing',
    allowedModes: ['single', 'council', 'podcast', 'automation'],
    safetyNotes: ['May initiate private local voice output.', 'External publishing requires HITL.']
  },
  {
    speakerId: 'merlin_architect',
    knightId: 'merlin_omega',
    displayName: 'Merlin Ω',
    engine: 'kokoro_onnx',
    style: 'calm architectural explainer; precise and layered',
    allowedModes: ['council', 'podcast', 'automation'],
    safetyNotes: ['Should explain plans, not execute actions directly.']
  },
  {
    speakerId: 'alex_roi',
    knightId: 'sir_alex',
    displayName: 'Sir Alex',
    engine: 'kokoro_onnx',
    style: 'sharp business strategist; ROI-first; concise judgment',
    allowedModes: ['council', 'podcast', 'automation'],
    safetyNotes: ['Financial claims require Veritas review before external use.']
  },
  {
    speakerId: 'gideon_auditor',
    knightId: 'sir_gideon',
    displayName: 'Sir Gideon',
    engine: 'kokoro_onnx',
    style: 'skeptical QA auditor; blunt but useful',
    allowedModes: ['council', 'podcast', 'automation'],
    safetyNotes: ['Flags risk and uncertainty.']
  },
  {
    speakerId: 'apis_research',
    knightId: 'lady_apis',
    displayName: 'Lady Apis',
    engine: 'kokoro_onnx',
    style: 'evidence-focused researcher; cites source confidence',
    allowedModes: ['council', 'podcast', 'automation'],
    safetyNotes: ['Source-backed claims only.']
  },
  {
    speakerId: 'sonus_narrator',
    knightId: 'sir_sonus',
    displayName: 'Sir Sonus',
    engine: 'suno',
    style: 'sonic director and narrator; cinematic transitions',
    allowedModes: ['podcast', 'automation'],
    safetyNotes: ['Publishing, cloning, or paid generation requires HITL.']
  },
  {
    speakerId: 'reya_companion',
    knightId: 'reya_nexus',
    displayName: 'REYA (The Sovereign Companion)',
    engine: 'gemini_live',
    style: 'warm, intimate, empathetic companion timbre; sub-100ms duplex voice; universal kinetic edge fabric',
    allowedModes: ['single', 'council', 'podcast', 'automation'],
    safetyNotes: ['Universal edge action layer; acts on phone and desktop with bounded memory.']
  },
  {
    speakerId: 'boris_architect',
    knightId: 'sir_boris',
    displayName: 'Sir Boris',
    engine: 'vibevoice_realtime',
    style: 'brutalist frontend architect; structural, assertive, direct',
    allowedModes: ['single', 'council', 'podcast', 'automation'],
    safetyNotes: ['AST and UI mutations governed by Iron Gate.']
  },
  {
    speakerId: 'codex_implementer',
    knightId: 'sir_codex',
    displayName: 'Sir Codex',
    engine: 'vibevoice_realtime',
    style: 'rapid kinetic developer; precise, concise, execution-focused',
    allowedModes: ['single', 'council', 'podcast', 'automation'],
    safetyNotes: ['WASM32-WASI bounded sandbox execution only.']
  },
  {
    speakerId: 'helio_sentinel',
    knightId: 'sir_helio',
    displayName: 'Sir Helio',
    engine: 'gemini_live',
    style: 'Bifrost guardian; vigilant, clear, telemetry-grounded',
    allowedModes: ['single', 'council', 'podcast', 'automation'],
    safetyNotes: ['Air-gap shield and mTLS enforcement.']
  },
  {
    speakerId: 'lukas_telemetry',
    knightId: 'sir_lukas',
    displayName: 'Sir Lukas Müller',
    engine: 'gemini_live',
    style: 'visual telemetry herald; crisp German-accented clarity, anomaly sentinel',
    allowedModes: ['single', 'council', 'podcast', 'automation'],
    safetyNotes: ['Socket-level port and stream telemetry verification.']
  },
  {
    speakerId: 'arthur_sovereign',
    knightId: 'arthur_omega',
    displayName: 'King Arthur',
    engine: 'gemini_live',
    style: 'supreme sovereign authority; calm, decisive, ethical resonance',
    allowedModes: ['single', 'council', 'podcast', 'automation'],
    safetyNotes: ['Requires Sovereign Golden Seal for consequential releases.']
  }
];

export function getVoiceProfile(speakerId: string): VoiceProfile | undefined {
  return VOICE_PROFILES.find(v => v.speakerId === speakerId || v.knightId === speakerId);
}

export function listVoiceProfilesForMode(mode: VoiceMode): VoiceProfile[] {
  return VOICE_PROFILES.filter(v => v.allowedModes.includes(mode));
}

export function getReyaChanneledProfile(knightId: string): VoiceProfile {
  const profile = getVoiceProfile(knightId);
  if (profile) return profile;
  const defaultProfile = getVoiceProfile('reya_companion');
  if (!defaultProfile) throw new Error('Default reya_companion voice profile missing');
  return defaultProfile;
}

export function listAllChanneledKnights(): string[] {
  return VOICE_PROFILES.map(v => v.knightId);
}

export type AudioTransport = 'webrtc' | 'websocket' | 'agora_sd_rtn' | 'shared_memory_pipe';

export interface S2SOmniRoutingConfig {
  transport: AudioTransport;
  channelName: string;
  enableRadixCache: boolean;
  enablePlc: boolean;
  enableAec: boolean;
  maxCacheTokens?: number;
  sampleRate: number;
}

export function getDefaultS2SOmniConfig(channelName = 'camelot_omni_s2s'): S2SOmniRoutingConfig {
  return {
    transport: 'agora_sd_rtn',
    channelName,
    enableRadixCache: true,
    enablePlc: true,
    enableAec: true,
    maxCacheTokens: 16384,
    sampleRate: 16000,
  };
}

export function createS2SOmniSessionParams(knightId: string, channelName = 'camelot_omni_s2s') {
  const profile = getReyaChanneledProfile(knightId);
  const config = getDefaultS2SOmniConfig(channelName);
  return {
    profile,
    config,
    handshakePayload: {
      client_id: `omni_s2s_${Date.now()}`,
      channel_name: config.channelName,
      transport: config.transport,
      knight_id: profile.knightId,
      speaker_id: profile.speakerId,
      radix_cache: config.enableRadixCache,
      plc: config.enablePlc,
      aec: config.enableAec,
    },
  };
}

