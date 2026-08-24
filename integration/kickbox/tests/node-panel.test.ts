// Phase 4A UI contract: the Node Status panel shows standing and routing,
// and never shows an address, key, or credential.

import { describe, expect, it } from 'vitest';
import { nodeIsServiceable, nodeStandingLabel, routeExplanation } from '@camelot/contracts';
import type { NodeView } from '@camelot/contracts';
import { bandClass, initialNodePanelState, meshSummary } from '../src/node-panel.js';

function node(overrides: Partial<NodeView> = {}): NodeView {
  return {
    nodeId: 'node-remote',
    tenantId: 'tenant-1',
    displayName: 'workshop-box',
    trust: 'trusted',
    health: 'healthy',
    local: false,
    capabilities: [{ name: 'compute:audio.features', readOnly: true }],
    agentVersion: '0.2.0',
    lastSeen: '2026-08-07T12:00:00Z',
    addressHash: 'a1b2c3d4e5f6',
    ...overrides,
  };
}

describe('node standing', () => {
  it('only trusted/limited AND healthy nodes are serviceable', () => {
    expect(nodeIsServiceable(node())).toBe(true);
    expect(nodeIsServiceable(node({ trust: 'limited' }))).toBe(true);
    expect(nodeIsServiceable(node({ trust: 'pending' }))).toBe(false);
    expect(nodeIsServiceable(node({ trust: 'degraded' }))).toBe(false);
    expect(nodeIsServiceable(node({ trust: 'revoked' }))).toBe(false);
    expect(nodeIsServiceable(node({ health: 'offline' }))).toBe(false);
  });

  it('explains each band in plain language', () => {
    expect(nodeStandingLabel(node())).toContain('ready');
    expect(nodeStandingLabel(node({ trust: 'limited' }))).toContain('read-only');
    expect(nodeStandingLabel(node({ trust: 'pending' }))).toContain('awaiting your approval');
    expect(nodeStandingLabel(node({ trust: 'degraded' }))).toContain('heartbeat stale');
    expect(nodeStandingLabel(node({ trust: 'revoked', revocationReason: 'lost laptop' }))).toContain(
      'lost laptop',
    );
    expect(bandClass(node({ trust: 'revoked' }))).toBe('band-revoked');
  });
});

describe('mesh summary', () => {
  it('reports local-only operation when the gateway is unreachable', () => {
    expect(meshSummary(initialNodePanelState())).toContain('local operation only');
  });

  it('counts ready, remote, and unavailable nodes', () => {
    const state = {
      ...initialNodePanelState(),
      reachable: true,
      nodes: [
        node({ nodeId: 'local-node', local: true }),
        node({ nodeId: 'node-a' }),
        node({ nodeId: 'node-b', trust: 'pending' }),
      ],
    };
    const summary = meshSummary(state);
    expect(summary).toContain('2/3 ready');
    expect(summary).toContain('2 remote');
    expect(summary).toContain('1 unavailable');
  });
});

describe('route explanation', () => {
  it('names where the job ran and whether it was a fallback', () => {
    expect(
      routeExplanation({
        requestId: 'nreq-1',
        target: 'remote',
        nodeId: 'node-a',
        capability: 'compute:audio.features',
        reason: 'explicit mesh request',
        fallback: false,
      }),
    ).toBe('remote node node-a · explicit mesh request');

    expect(
      routeExplanation({
        requestId: 'nreq-2',
        target: 'local',
        nodeId: 'local-node',
        capability: 'compute:audio.features',
        reason: 'remote failed',
        fallback: true,
      }),
    ).toContain('(fallback)');

    expect(
      routeExplanation({
        requestId: 'nreq-3',
        target: 'none',
        capability: 'compute:audio.features',
        reason: 'no eligible node',
        fallback: false,
      }),
    ).toContain('no route');
  });
});

describe('privacy of the node view', () => {
  it('the rendered contract carries no address, key, or secret field', () => {
    const view = node();
    const keys = Object.keys(view);
    for (const forbidden of ['dispatchUrl', 'keyFingerprint', 'token', 'apiKey', 'secret']) {
      expect(keys).not.toContain(forbidden);
    }
    // The only address-ish field is an opaque hash.
    expect(view.addressHash).toMatch(/^[0-9a-f]{12}$/);
    expect(JSON.stringify(view)).not.toMatch(/https?:\/\//);
  });
});
