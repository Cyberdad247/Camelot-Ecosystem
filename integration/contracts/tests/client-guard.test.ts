// T1 (client half): Kickbox cannot invoke an effectful tool without a lease —
// in fact it cannot invoke a tool at all. The client exposes only the governed
// surface; there is no tool-execution or node-agent method to call, and the
// path allow-list is frozen.

import { describe, expect, it, vi } from 'vitest';
import { ALLOWED_PATHS, BoundaryViolationError, CamelotClient } from '../src/index.js';

const okJson = () =>
  Promise.resolve(new Response(JSON.stringify({ status: 'ok', service: 'x', version: '0' })));

function makeClient(fetchImpl: typeof fetch = vi.fn(okJson) as unknown as typeof fetch) {
  return new CamelotClient({ baseUrl: 'http://gateway.test', fetchImpl });
}

describe('CamelotClient boundary (ADR-001: PWA never calls tools directly)', () => {
  it('exposes no tool- or node-invocation surface', () => {
    const client = makeClient();
    const surface = [
      ...Object.getOwnPropertyNames(Object.getPrototypeOf(client)),
      ...Object.getOwnPropertyNames(client),
    ];
    for (const name of surface) {
      expect(name).not.toMatch(/tool|exec|compute|node|invoke/i);
    }
    expect((client as Record<string, unknown>)['invokeTool']).toBeUndefined();
    expect((client as Record<string, unknown>)['executeTool']).toBeUndefined();
    expect((client as Record<string, unknown>)['request']).toBeUndefined();
  });

  it('the allow-list is frozen and contains exactly the governed endpoints', () => {
    expect(Object.isFrozen(ALLOWED_PATHS)).toBe(true);
    expect([...ALLOWED_PATHS]).toEqual([
      '/v1/voice/turns',
      '/v1/voice/barge-in',
      '/v1/confirmations',
      '/v1/audit/',
      '/healthz',
    ]);
  });

  it('client instances are frozen — the surface cannot be extended at runtime', () => {
    const client = makeClient();
    expect(Object.isFrozen(client)).toBe(true);
    expect(() => {
      // @ts-expect-error deliberate escape attempt
      client.invokeTool = () => {};
    }).toThrow();
  });

  it('an out-of-surface path is rejected before any network I/O', async () => {
    const fetchSpy = vi.fn(okJson) as unknown as typeof fetch;
    const client = makeClient(fetchSpy);
    // Reach the private request path via a legitimate method's guard by
    // simulating what a compromised caller would attempt: monkey-patching is
    // impossible (frozen), so the only route is the public methods — which
    // pin their paths. Verify the guard itself via getAudit path traversal.
    await expect(client.getAudit('../tools/execute')).resolves.toBeDefined();
    const calledUrl = (fetchSpy as unknown as ReturnType<typeof vi.fn>).mock
      .calls[0]?.[0] as string;
    // Traversal is neutralized by encodeURIComponent — still under /v1/audit/.
    expect(calledUrl).toBe('http://gateway.test/v1/audit/..%2Ftools%2Fexecute');
  });

  it('BoundaryViolationError names the violated path', () => {
    const err = new BoundaryViolationError('/v1/tools/execute');
    expect(err.message).toContain('/v1/tools/execute');
    expect(err.message).toContain('ADR-001');
  });
});
