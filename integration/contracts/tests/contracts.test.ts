import { describe, expect, it } from 'vitest';
import {
  FIXTURE_UTTERANCES,
  INTENT_FIXTURES,
  fixtureTurn,
  matchIntent,
  mockBargeIn,
} from '../src/index.js';
import type { CamelotTurnResponse, VoiceTurn } from '../src/index.js';

describe('intent fixtures (deterministic, no API keys)', () => {
  it('maps the three demo utterances to the three bootstrap skills', () => {
    expect(matchIntent(FIXTURE_UTTERANCES.stagingRead)?.skillId).toBe('ops.staging.read');
    expect(matchIntent(FIXTURE_UTTERANCES.deploymentReview)?.skillId).toBe(
      'deployment.review.prepare',
    );
    expect(matchIntent(FIXTURE_UTTERANCES.changeRequest)?.skillId).toBe('change_request.create');
  });

  it('is case-insensitive and returns null for small talk', () => {
    expect(matchIntent('READ STAGING STATUS')?.skillId).toBe('ops.staging.read');
    expect(matchIntent('hello anya, how are you?')).toBeNull();
  });

  it('the most specific match wins when keywords overlap', () => {
    expect(matchIntent('prepare a staging deployment review and explain the risk')?.skillId).toBe(
      'deployment.review.prepare',
    );
  });

  it('declares governance tiers exactly as ADR-001 specifies', () => {
    const byId = Object.fromEntries(INTENT_FIXTURES.map((f) => [f.skillId, f]));
    expect(byId['ops.staging.read']).toMatchObject({
      tier: 1,
      effectful: false,
      confirmationRequired: false,
    });
    expect(byId['deployment.review.prepare']).toMatchObject({
      tier: 2,
      effectful: true,
      confirmationRequired: false,
    });
    expect(byId['change_request.create']).toMatchObject({
      tier: 3,
      effectful: true,
      confirmationRequired: true,
    });
  });
});

describe('turn fixtures', () => {
  it('produces deterministic ids and timestamps', () => {
    const a = fixtureTurn('read staging status', 1);
    const b = fixtureTurn('read staging status', 1);
    expect(a).toEqual(b);
    expect(a.turnId).toBe('turn-0001');
    expect(a.modality).toBe('text');
  });

  it('mock barge-in targets the interrupted turn with reason "mock"', () => {
    const bargeIn = mockBargeIn('turn-0002');
    expect(bargeIn.turnId).toBe('turn-0002');
    expect(bargeIn.reason).toBe('mock');
  });

  it('never carries raw audio — only an optional hash field exists', () => {
    const turn = fixtureTurn('read staging status', 3);
    expect('audio' in turn).toBe(false);
    expect('samples' in turn).toBe(false);
    const keys: Array<keyof VoiceTurn> = Object.keys(turn) as Array<keyof VoiceTurn>;
    for (const k of keys) expect(k).not.toMatch(/pcm|buffer|blob/i);
  });
});

describe('wire-format round trips', () => {
  it('CamelotTurnResponse survives JSON round trip', () => {
    const response: CamelotTurnResponse = {
      sessionId: 'sess-anya-demo-001',
      turnId: 'turn-0001',
      uiState: 'speaking',
      decision: {
        decisionId: 'dec-1',
        effect: 'allow',
        skillId: 'ops.staging.read',
        tier: 1,
        reason: 'tier-1 read-only skill',
        policyVersion: 'v1',
        decidedAt: '2026-08-07T00:00:00Z',
      },
      reply: { text: 'staging is green', final: false },
      auditId: 'audit-1',
    };
    expect(JSON.parse(JSON.stringify(response))).toEqual(response);
  });
});
