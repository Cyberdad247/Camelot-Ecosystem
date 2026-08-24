// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY

// packages/anya-domain/src/ironGate.ts
import { z } from 'zod';

export const IronGateRiskLevelSchema = z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']);
export type IronGateRiskLevel = z.infer<typeof IronGateRiskLevelSchema>;

// VOICE INTENT DICTIONARY [Chronos's Amendment: Safety Allow-list]
export const VoiceIntentSchema = z.enum([
  'OPEN_TERMINAL',
  'CLOSE_SESSION',
  'RUN_TRIVY_SCAN',
  'TOGGLE_HUD',
  'REQUEST_SYSTEM_STATUS'
]);
export type VoiceIntent = z.infer<typeof VoiceIntentSchema>;

export const IronGateChallengeSchema = z.object({
  kind: z.literal('IRON_GATE_CHALLENGE'),
  reason: z.string(),
  timestamp: z.number(), // Unix timestamp [Arthur's Amendment]
  nonce: z.string(),     // Anti-replay nonce [Arthur's Amendment]
  riskLevel: IronGateRiskLevelSchema,
});

export const IronGateResponseSchema = z.object({
  verified: z.boolean(),
  signature: z.string().optional(),
  deviceId: z.string(),
  timestamp: z.number(),
  nonce: z.string(),
});

// Exported for titanLink.ts discriminated unions
export const IronGateApprovalRequestSchema = z.object({
  kind: z.literal('iron_gate_approval_request'),
  actionId: z.string(),
  reason: z.string(),
  timestamp: z.number(),
  nonce: z.string(),
  riskLevel: IronGateRiskLevelSchema,
});

export const IronGateApprovalResponseSchema = z.object({
  kind: z.literal('iron_gate_approval_response'),
  actionId: z.string(),
  approved: z.boolean(),
  signature: z.string().optional(),
  timestamp: z.number(),
  nonce: z.string(),
});

// MOLTBOT GATEWAY LOGIC [Assimilated Gateway Guardian]
export class MoltbotGateway {
  static assessRisk(intent: string): IronGateRiskLevel {
    // [Arthur's Amendment]: Mandatory HIGH for Remote Access
    const mandatoryHighRisk = ['remote', 'root', 'sudo', 'login', 'session'];
    const query = intent.toLowerCase();

    if (mandatoryHighRisk.some(kw => query.includes(kw))) {
      return 'HIGH';
    }

    const medRiskKeywords = ['delete', 'transfer', 'update'];
    if (medRiskKeywords.some(kw => query.includes(kw))) {
      return 'MEDIUM';
    }

    return 'LOW';
  }

  static async verifySignature(challenge: z.infer<typeof IronGateChallengeSchema>, response: z.infer<typeof IronGateResponseSchema>, publicKey: string): Promise<boolean> {
    // [Arthur's Amendment]: 30s TTL Verification
    const now = Date.now() / 1000;
    if (now - challenge.timestamp > 30) {
      console.error("⛔ IRON GATE: Challenge STALE (>30s). Rejected.");
      return false;
    }

    // Nonce mismatch check
    if (challenge.nonce !== response.nonce) {
      console.error("⛔ IRON GATE: Nonce mismatch. Replay detected.");
      return false;
    }

    // In production: Use WebCrypto API for real cryptographic verification
    console.log("🛡️ MOLTBOT: Verifying Biometric Signature...");
    return !!(response.signature && publicKey);
  }
}

export async function enforceBiometricGate(intent: string, titanLink: { send: (payload: unknown) => Promise<unknown> }) {
  const risk = MoltbotGateway.assessRisk(intent);

  if (risk === 'HIGH' || risk === 'CRITICAL') {
    console.log(`🔒 IRON GATE: High Risk Intent Detected [${intent}]. Triggering Biometric Challenge...`);

    // Generate ephemeral challenge data
    const challengePayload = {
      kind: 'IRON_GATE_CHALLENGE' as const,
      reason: `Remote Access Required for: ${intent}`,
      riskLevel: risk,
      timestamp: Math.floor(Date.now() / 1000),
      nonce: Math.random().toString(36).substring(7)
    };

    const response = await titanLink.send(challengePayload);

    const isVerified = await MoltbotGateway.verifySignature(challengePayload, response, "SOVEREIGN_PUB_KEY");

    if (!isVerified) {
      throw new Error("⛔ IRON GATE: Biometrics Rejected. Unauthorized Access Blocked.");
    }
  }
  return true;
}