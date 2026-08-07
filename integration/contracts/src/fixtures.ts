// Deterministic fixtures for the no-API-key demo and for tests.
//
// The gateway's Hermes adapter (integration/gateway/hermes.go) mirrors
// INTENT_FIXTURES exactly — if you change a phrase or skill mapping here,
// change it there too (T-fixture parity is asserted in gateway tests).

import type { SkillTier, VoiceBargeIn, VoiceTurn } from './types.js';

export const FIXTURE_SESSION_ID = 'sess-anya-demo-001';

export interface IntentFixture {
  /** Lower-cased keyword that selects this intent when present in the transcript. */
  match: string;
  skillId: string;
  tier: SkillTier;
  effectful: boolean;
  confirmationRequired: boolean;
}

/** Bootstrap skills (ADR-001 / bootstrap-plan §3). Order matters: first match wins. */
export const INTENT_FIXTURES: readonly IntentFixture[] = [
  {
    match: 'staging',
    skillId: 'ops.staging.read',
    tier: 1,
    effectful: false,
    confirmationRequired: false,
  },
  {
    match: 'deployment review',
    skillId: 'deployment.review.prepare',
    tier: 2,
    effectful: true,
    confirmationRequired: false,
  },
  {
    match: 'change request',
    skillId: 'change_request.create',
    tier: 3,
    effectful: true,
    confirmationRequired: true,
  },
] as const;

/** Demo utterances wired to the three bootstrap skills. */
export const FIXTURE_UTTERANCES = {
  stagingRead: 'read staging status',
  deploymentReview: 'prepare a deployment review for the voice slice',
  changeRequest: 'create a change request to scale the api tier',
} as const;

/** Resolve a transcript to an intent fixture, or null for small talk.
 *  Longest match wins (mirrors gateway hermes.go): "prepare a staging
 *  deployment review" is the tier-2 review skill, not the staging read. */
export function matchIntent(transcript: string): IntentFixture | null {
  const t = transcript.toLowerCase();
  let best: IntentFixture | null = null;
  for (const f of INTENT_FIXTURES) {
    if (t.includes(f.match) && (best === null || f.match.length > best.match.length)) {
      best = f;
    }
  }
  return best;
}

/** Build a deterministic text-first turn. `n` numbers the turn within the session. */
export function fixtureTurn(transcript: string, n: number, sessionId = FIXTURE_SESSION_ID): VoiceTurn {
  return {
    sessionId,
    turnId: `turn-${String(n).padStart(4, '0')}`,
    modality: 'text',
    transcript,
    startedAtMs: 1_754_000_000_000 + n * 10_000,
    endedAtMs: 1_754_000_000_000 + n * 10_000 + 1_500,
    locale: 'en-US',
  };
}

/** The mock barge-in event used by the Console's barge-in control. */
export function mockBargeIn(turnId: string, sessionId = FIXTURE_SESSION_ID): VoiceBargeIn {
  return {
    sessionId,
    turnId,
    atMs: 1_754_000_099_000,
    reason: 'mock',
  };
}
