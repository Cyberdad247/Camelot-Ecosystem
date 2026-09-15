export interface NodeRecord {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'syncing' | 'isolated' | 'ACTIVE';
  ip: string;
  load: number;
  lastSeen: number;
  coordinates?: { x: number; y: number };
}

export interface TelemetryData {
  timestamp: number;
  globalLoad: number;
  activeLeases: number;
  networkEgress: number;
  ramUsageMB: number;
  ramCeilingMB: number;
  ramPercent: number;
  madvReclaimedMB: number;
  hardwareCeiling: string;
  alerts: string[];
}

export type CartridgeId = 'excalibur-ecc' | 'ecosystem-pwa' | 'kba-executive' | 'digital-factory' | '1vizion-rcrds';

export interface CartridgeMetadata {
  id: CartridgeId;
  code: string;
  name: string;
  tagline: string;
  type: string;
  risk: 'R0' | 'R1' | 'R2' | 'R3' | 'R4' | 'R5';
  status: 'LOCKED' | 'UNLOCKED' | 'ACTIVE';
  description: string;
  category: string;
  capabilities: string[];
}

export interface BioAuthState {
  faceScanned: boolean;
  faceVector: number[];
  voiceScanned: boolean;
  voicePhrase: string;
  challengeRotationCode: string;
  qrBound: boolean;
  deviceSignature: string;
  fido2KnoxEnclaveBound: boolean;
  challengeId: string;
  challengeNonce: string;
  isAuthenticating: boolean;
  authenticated: boolean;
  leaseId: string | null;
  operator: string;
  vaultMatched: boolean;
}
