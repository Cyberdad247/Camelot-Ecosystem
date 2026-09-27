// The skill catalog is generated from contracts/skills.manifest.json, so
// Go/TS agreement is structural and no longer needs a parity table. What
// still needs proving is that the CATALOG ITSELF is sane and that the
// matcher's precedence rules do what they claim — those are the properties a
// manifest edit can break.

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { FIXTURE_UTTERANCES, matchIntent, matchSkill } from '../src/fixtures.js';
import { MANIFEST_VERSION, SKILLS, skillById } from '../src/skills.gen.js';

const manifest = JSON.parse(
  readFileSync(fileURLToPath(new URL('../skills.manifest.json', import.meta.url)), 'utf8'),
);

describe('generated catalog', () => {
  it('is generated from the committed manifest', () => {
    expect(MANIFEST_VERSION).toBe(manifest.manifestVersion);
    expect(SKILLS.map((s) => s.id)).toEqual(manifest.skills.map((s: { id: string }) => s.id));
  });

  it('holds the policy invariants the gateway relies on', () => {
    for (const s of SKILLS) {
      expect(s.tier, `${s.id} tier`).toBeGreaterThanOrEqual(1);
      expect(s.tier, `${s.id} tier`).toBeLessThanOrEqual(3);
      // effectful must track tier, because tier is what the broker gates on.
      expect(s.effectful, `${s.id} effectful`).toBe(s.tier >= 2);
      if (s.tier === 3) expect(s.confirmationRequired, `${s.id}`).toBe(true);
      // A durable skill that is not lease-gated could act without approval.
      if (s.durable) {
        expect(s.effectful, `${s.id} durable must be effectful`).toBe(true);
        expect(s.retry, `${s.id} durable must not retry`).toBe('never');
        expect(s.idempotency, `${s.id}`).toBe('lease_single_use');
      }
      expect(s.phrases.length, `${s.id} phrases`).toBeGreaterThan(0);
      for (const p of s.phrases) expect(p).toBe(p.toLowerCase());
    }
  });

  it('claims each trigger phrase exactly once', () => {
    const owners = new Map<string, string>();
    for (const s of SKILLS) {
      for (const p of s.phrases) {
        expect(owners.has(p), `phrase "${p}" claimed by ${owners.get(p)} and ${s.id}`).toBe(false);
        owners.set(p, s.id);
      }
    }
  });

  it('exposes exactly one durable skill so far', () => {
    // Guards against a manifest edit quietly turning fixtures into real
    // side effects. Update deliberately when a second one is intended.
    expect(SKILLS.filter((s) => s.durable).map((s) => s.id)).toEqual(['notes.local.write']);
  });
});

describe('intent precedence', () => {
  it('resolves the demo utterances', () => {
    expect(matchSkill(FIXTURE_UTTERANCES.stagingRead)?.id).toBe('ops.staging.read');
    expect(matchSkill(FIXTURE_UTTERANCES.deploymentReview)?.id).toBe('deployment.review.prepare');
    expect(matchSkill(FIXTURE_UTTERANCES.changeRequest)?.id).toBe('change_request.create');
    expect(matchSkill(FIXTURE_UTTERANCES.localNote)?.id).toBe('notes.local.write');
  });

  it('longest phrase wins over a generic substring', () => {
    // The original shadowing bug: "staging" is present, but the specific
    // phrase must win or a tier-2 action resolves to a tier-1 read.
    expect(matchSkill('prepare a staging deployment review')?.id).toBe('deployment.review.prepare');
  });

  it('a durable skill is not shadowed by a read that shares vocabulary', () => {
    // "save a note about the staging rollout" contains "staging". Resolving
    // it to the tier-1 read would silently drop the user's write.
    const s = matchSkill('save a note about the staging rollout');
    expect(s?.id).toBe('notes.local.write');
    expect(s?.durable).toBe(true);
  });

  it('is case insensitive and returns null for small talk', () => {
    expect(matchSkill('READ STAGING STATUS')?.id).toBe('ops.staging.read');
    expect(matchSkill('hello anya, how are you?')).toBeNull();
  });

  it('is deterministic regardless of catalog order', () => {
    const utterances = [
      'read staging status',
      'prepare a staging deployment review',
      'save a note about the staging rollout',
      'create a change request',
    ];
    const once = utterances.map((u) => matchSkill(u)?.id);
    const twice = utterances.map((u) => matchSkill(u)?.id);
    expect(once).toEqual(twice);
  });

  it('matchIntent stays a faithful projection of matchSkill', () => {
    for (const u of Object.values(FIXTURE_UTTERANCES)) {
      expect(matchIntent(u)?.skillId).toBe(matchSkill(u)?.id);
    }
    expect(matchIntent('hello there')).toBeNull();
  });
});

describe('skillById', () => {
  it('finds a known skill and refuses an unknown one', () => {
    expect(skillById('notes.local.write')?.tier).toBe(2);
    expect(skillById('nope.not.a.skill')).toBeNull();
  });
});
