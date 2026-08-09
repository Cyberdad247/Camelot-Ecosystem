// Deterministic fixtures for the no-API-key demo and for tests.
//
// The skill catalog itself is GENERATED from contracts/skills.manifest.json
// into skills.gen.ts, and the Go gateway generates its registry from the same
// manifest. The two can no longer drift, so the hand-maintained parity table
// this file used to require is gone.

import type { SkillTier, VoiceBargeIn, VoiceTurn } from './types.js';
import { SKILLS, type SkillDefinition } from './skills.gen.js';

export { SKILLS, skillById, MANIFEST_VERSION, MANIFEST_POLICY_VERSION } from './skills.gen.js';
export type { SkillDefinition, SkillEffect } from './skills.gen.js';

export const FIXTURE_SESSION_ID = 'sess-anya-demo-001';

export interface IntentFixture {
  /** Lower-cased keyword that selects this intent when present in the transcript. */
  match: string;
  skillId: string;
  tier: SkillTier;
  effectful: boolean;
  confirmationRequired: boolean;
}

/** Bootstrap skills, projected from the generated catalog. Kept for the
 *  existing consumers; new code should read SKILLS directly. */
export const INTENT_FIXTURES: readonly IntentFixture[] = SKILLS.map((s) => ({
  match: s.phrases[0] as string,
  skillId: s.id,
  tier: s.tier,
  effectful: s.effectful,
  confirmationRequired: s.confirmationRequired,
}));

/** Demo utterances wired to the bootstrap skills. */
export const FIXTURE_UTTERANCES = {
  stagingRead: 'read staging status',
  deploymentReview: 'prepare a deployment review for the voice slice',
  changeRequest: 'create a change request to scale the api tier',
  localNote: 'save a note about the staging rollout',
} as const;

/** Resolve a transcript to a skill, or null for small talk.
 *
 *  Mirrors hermesMatchIntent in gateway/hermes.go exactly, including the
 *  tie-breaks: longest matching phrase, then higher priority, then lexically
 *  lower id. Both sides read the same generated catalog, so agreement is
 *  structural rather than asserted. */
export function matchSkill(transcript: string): SkillDefinition | null {
  const t = transcript.toLowerCase();
  let best: SkillDefinition | null = null;
  let bestLen = 0;
  for (const s of SKILLS) {
    for (const phrase of s.phrases) {
      if (!t.includes(phrase)) continue;
      const better =
        phrase.length > bestLen ||
        (phrase.length === bestLen && best !== null && s.priority > best.priority) ||
        (phrase.length === bestLen && best !== null && s.priority === best.priority && s.id < best.id);
      if (best === null || better) {
        best = s;
        bestLen = phrase.length;
      }
    }
  }
  return best;
}

/** Back-compat projection of matchSkill onto the older fixture shape. */
export function matchIntent(transcript: string): IntentFixture | null {
  const s = matchSkill(transcript);
  if (s === null) return null;
  return {
    match: s.phrases[0] as string,
    skillId: s.id,
    tier: s.tier,
    effectful: s.effectful,
    confirmationRequired: s.confirmationRequired,
  };
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
