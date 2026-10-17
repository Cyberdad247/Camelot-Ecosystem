import { describe, expect, it } from 'vitest';
import { determineRoute, resolveKnightEngine } from './policy';

describe('OmniRoute Policy', () => {
  it('should route high-context tasks to Gemini', () => {
    const target = determineRoute({ contextSize: 150000, taskType: 'analysis' });
    expect(target).toBe('OmniRoute/gemini');
  });

  it('should route kinetic code generation to Claude', () => {
    const target = determineRoute({ contextSize: 5000, taskType: 'kinetic_code_generation' });
    expect(target).toBe('OmniRoute/anthropic');
  });

  it('should route stealth foraging to proxy stream', () => {
    const target = determineRoute({ contextSize: 1000, taskType: 'stealth_web_foraging' });
    expect(target).toBe('OmniRoute/proxy/stream');
  });

  it('should route secrets or privacy tasks to Sir Ghost air-gap', () => {
    const target = determineRoute({
      contextSize: 200,
      taskType: 'secret_scan',
      containsSecrets: true,
    });
    expect(target).toBe('OmniRoute/sir_ghost');
  });

  it('should resolve Knight engine bindings accurately', () => {
    const res = resolveKnightEngine({ contextSize: 2000, taskType: 'kinetic_code_generation' });
    expect(res.knightId).toBe('SIR_BORIS');
    expect(res.engineTarget).toBe('claude-3-7-sonnet');
  });
});
